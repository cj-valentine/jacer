using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;
using NUnit.Framework;

namespace Jacer.E2E;

/// <summary>
/// End-to-end for the Phase 3.5 templates editor: create a template, add an
/// untimed tick-off item in the Monday column, lock it, and let the board's
/// on-load materialisation surface the task; plus the click-away-save fix.
/// Migrated from the Phase 3 band-grid flow (placeholder "Title…" → "Tick-off
/// task…"; items are untimed by default).
/// Requires the frontend (JACER_WEB_URL) and backend running.
/// </summary>
[Parallelizable(ParallelScope.Self)]
[TestFixture]
public class TemplatesFlowTests : PageTest
{
    private static string BaseUrl =>
        Environment.GetEnvironmentVariable("JACER_WEB_URL") ?? "http://localhost:5099";

    private async Task CreateTemplateAsync()
    {
        await Page.GetByRole(AriaRole.Button, new() { Name = "New template" }).ClickAsync();
        var nameField = Page.GetByPlaceholder("Template name…");
        await Expect(nameField).ToBeEnabledAsync(new() { Timeout = 15_000 });
        await nameField.FillAsync($"E2E week {Guid.NewGuid():N}");
        await nameField.PressAsync("Enter");
    }

    [Test]
    public async Task Create_template_add_item_lock_then_board_materialises_it()
    {
        var itemTitle = $"E2E routine {Guid.NewGuid():N}";

        await Page.GotoAsync($"{BaseUrl}/templates", new() { WaitUntil = WaitUntilState.NetworkIdle });
        await CreateTemplateAsync();

        // Add an untimed item in the first (Monday) column.
        var addButton = Page.GetByRole(AriaRole.Button, new() { Name = "Add" }).First;
        await Expect(addButton).ToBeVisibleAsync(new() { Timeout = 15_000 });
        await addButton.ClickAsync();

        var titleField = Page.GetByPlaceholder("Tick-off task…");
        await titleField.FillAsync(itemTitle);
        await titleField.PressAsync("Enter");

        await Expect(Page.GetByText(itemTitle).First).ToBeVisibleAsync(new() { Timeout = 15_000 });
        await Page.GetByRole(AriaRole.Button, new() { Name = "Lock", Exact = true }).ClickAsync();

        // The board's 14-day horizon materialise covers the next Monday, so the
        // locked item's task appears somewhere on the board (today or Upcoming).
        await Page.GotoAsync(BaseUrl, new() { WaitUntil = WaitUntilState.NetworkIdle });
        await Expect(Page.GetByText(itemTitle).First).ToBeVisibleAsync(new() { Timeout = 15_000 });
    }

    [Test]
    public async Task Clicking_away_from_a_new_template_item_saves_it()
    {
        var itemTitle = $"Click-away {Guid.NewGuid():N}";

        await Page.GotoAsync($"{BaseUrl}/templates", new() { WaitUntil = WaitUntilState.NetworkIdle });
        await CreateTemplateAsync();

        var addButton = Page.GetByRole(AriaRole.Button, new() { Name = "Add" }).First;
        await Expect(addButton).ToBeVisibleAsync(new() { Timeout = 15_000 });
        await addButton.ClickAsync();

        var titleField = Page.GetByPlaceholder("Tick-off task…");
        await titleField.FillAsync(itemTitle);

        // Click away WITHOUT pressing Enter — the blur must save, not discard.
        await Page.GetByRole(AriaRole.Heading, new() { Name = "Templates" }).ClickAsync();

        await Expect(Page.GetByText(itemTitle).First).ToBeVisibleAsync(new() { Timeout = 15_000 });
    }
}
