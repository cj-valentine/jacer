using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;
using NUnit.Framework;

namespace Jacer.E2E;

/// <summary>
/// One end-to-end smoke test: loads the board and exercises the interactive
/// quick-add path (Blazor Server circuit → backend POST → re-render).
/// Requires the frontend (JACER_WEB_URL, default http://localhost:5099) and the
/// backend to be running, plus Playwright browsers installed
/// (`pwsh bin/Debug/net10.0/playwright.ps1 install chromium`).
/// </summary>
[Parallelizable(ParallelScope.Self)]
[TestFixture]
public class BoardSmokeTests : PageTest
{
    private static string BaseUrl =>
        Environment.GetEnvironmentVariable("JACER_WEB_URL") ?? "http://localhost:5099";

    [Test]
    public async Task Board_loads_and_quick_add_creates_a_task()
    {
        await Page.GotoAsync(BaseUrl, new() { WaitUntil = WaitUntilState.NetworkIdle });

        // Board heading and the drag-and-drop container render. Use the heading
        // role — the app bar also has a "Board" nav link, so plain text is ambiguous.
        await Expect(Page.GetByRole(AriaRole.Heading, new() { Name = "Board" })).ToBeVisibleAsync();
        await Expect(Page.Locator(".mud-drop-container")).ToBeVisibleAsync();

        // The quick-add field is disabled until the board's first load completes;
        // waiting for it to be enabled confirms the interactive circuit is live.
        var quickAdd = Page.GetByPlaceholder("Add a task and press Enter…");
        await Expect(quickAdd).ToBeEnabledAsync(new() { Timeout = 15_000 });

        // A unique title means the assertion below matches exactly one element.
        var title = $"Smoke task {Guid.NewGuid():N}";
        await quickAdd.FillAsync(title);
        await quickAdd.PressAsync("Enter");

        await Expect(Page.GetByText(title)).ToBeVisibleAsync(new() { Timeout = 15_000 });
    }
}
