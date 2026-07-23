using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;
using NUnit.Framework;

namespace Jacer.E2E;

/// <summary>
/// Board smoke: the day-centric board loads (week strip + quick-add) and the
/// interactive circuit is live (quick-add creates a task). Migrated from the
/// Phase 3 Kanban smoke — the old `.mud-drop-container` is gone; the week strip
/// is the day-centric board's load marker.
/// Requires the frontend (JACER_WEB_URL, default http://localhost:5099) and the
/// backend running, plus Playwright browsers installed.
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

        await Expect(Page.GetByRole(AriaRole.Heading, new() { Name = "Board" })).ToBeVisibleAsync();
        await Expect(Page.Locator(".week-strip")).ToBeVisibleAsync(new() { Timeout = 15_000 });

        var quickAdd = Page.GetByPlaceholder("Add a task and press Enter…");
        await Expect(quickAdd).ToBeEnabledAsync(new() { Timeout = 15_000 });

        var title = $"Smoke task {Guid.NewGuid():N}";
        await quickAdd.FillAsync(title);
        await quickAdd.PressAsync("Enter");

        await Expect(Page.GetByText(title)).ToBeVisibleAsync(new() { Timeout = 15_000 });
    }
}
