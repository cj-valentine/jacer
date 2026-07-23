using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;
using NUnit.Framework;

namespace Jacer.E2E;

/// <summary>
/// End-to-end for the Phase 3 templates loop: create a template, add an item,
/// lock it, then let the board's on-load materialisation surface the task.
/// Requires the frontend (JACER_WEB_URL, default http://localhost:5099) and the
/// backend running, plus Playwright browsers installed.
/// </summary>
[Parallelizable(ParallelScope.Self)]
[TestFixture]
public class TemplatesFlowTests : PageTest
{
    private static string BaseUrl =>
        Environment.GetEnvironmentVariable("JACER_WEB_URL") ?? "http://localhost:5099";

    [Test]
    public async Task Create_template_add_item_lock_then_board_materialises_it()
    {
        var itemTitle = $"E2E routine {Guid.NewGuid():N}";

        await Page.GotoAsync($"{BaseUrl}/templates", new() { WaitUntil = WaitUntilState.NetworkIdle });

        // Create a fresh template (works whether or not templates already exist).
        await Page.GetByRole(AriaRole.Button, new() { Name = "New template" }).ClickAsync();
        var nameField = Page.GetByPlaceholder("Template name…");
        await Expect(nameField).ToBeEnabledAsync(new() { Timeout = 15_000 });
        await nameField.FillAsync($"E2E week {Guid.NewGuid():N}");
        await nameField.PressAsync("Enter");

        // The first grid cell is Monday / Morning. Add an item there.
        var addButton = Page.GetByRole(AriaRole.Button, new() { Name = "Add" }).First;
        await Expect(addButton).ToBeVisibleAsync(new() { Timeout = 15_000 });
        await addButton.ClickAsync();

        var titleField = Page.GetByPlaceholder("Title…");
        await titleField.FillAsync(itemTitle);
        await titleField.PressAsync("Enter");

        // The item shows in the grid, then lock the template.
        await Expect(Page.GetByText(itemTitle).First).ToBeVisibleAsync(new() { Timeout = 15_000 });
        await Page.GetByRole(AriaRole.Button, new() { Name = "Lock", Exact = true }).ClickAsync();

        // Loading the board fires the 14-day horizon materialise; a Monday always
        // falls within the horizon, so the locked item's task appears on the board.
        await Page.GotoAsync(BaseUrl, new() { WaitUntil = WaitUntilState.NetworkIdle });
        await Expect(Page.GetByText(itemTitle).First).ToBeVisibleAsync(new() { Timeout = 15_000 });
    }
}
