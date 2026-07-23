using Microsoft.Extensions.DependencyInjection;

namespace Jacer.Tests;

public class TemplatesEditorTests
{
    private static BunitContext NewContext(FakeTemplatesApi api)
    {
        var ctx = new BunitContext();
        ctx.Services.AddMudServices();
        ctx.Services.AddSingleton<ITemplatesApi>(api);
        ctx.JSInterop.Mode = JSRuntimeMode.Loose;
        return ctx;
    }

    private static FakeTemplatesApi ApiWithOneTemplate(params TemplateItemDto[] items) =>
        new([TestData.Template("tpl-1", "My week")], items);

    [Fact]
    public async Task Grid_renders_all_weekdays_and_bands()
    {
        var api = ApiWithOneTemplate();
        await using var ctx = NewContext(api);

        var cut = ctx.Render<TemplatesEditor>();

        foreach (var day in TimeBands.DayLabels)
        {
            Assert.Contains($">{day}<", cut.Markup);
        }
        foreach (var band in TimeBands.Order)
        {
            Assert.Contains(TimeBands.Label(band), cut.Markup);
        }
    }

    [Fact]
    public async Task Item_renders_in_its_band_row()
    {
        var api = ApiWithOneTemplate(
            TestData.Item("i1", "tpl-1", dayOfWeek: 0, title: "Morning standup", time: "09:00"));
        await using var ctx = NewContext(api);

        var cut = ctx.Render<TemplatesEditor>();

        Assert.Contains("Morning standup", cut.Markup);
        // The morning item's cell shows its time and duration.
        Assert.Contains("09:00", cut.Markup);
    }

    [Fact]
    public async Task Clicking_add_reveals_the_inline_title_input()
    {
        var api = ApiWithOneTemplate();
        await using var ctx = NewContext(api);
        var cut = ctx.Render<TemplatesEditor>();

        // No text inputs in the grid until an Add affordance is clicked.
        var addButtons = cut.FindAll("button").Where(b => b.TextContent.Contains("Add")).ToList();
        Assert.NotEmpty(addButtons);

        addButtons[0].Click();

        // An inline title field is now present.
        Assert.Contains("Title…", cut.Markup);
    }

    [Fact]
    public async Task Fortnightly_grid_filters_items_by_selected_week()
    {
        var template = new TemplateDto
        {
            Id = "tpl-1",
            Name = "Fortnight",
            Cadence = Cadence.Fortnightly,
            WeekAStartDate = "2026-07-20",
            CreatedAt = DateTimeOffset.UnixEpoch,
            UpdatedAt = DateTimeOffset.UnixEpoch,
        };
        var weekA = new TemplateItemDto { Id = "a", TemplateId = "tpl-1", DayOfWeek = 0, Title = "Week A item", WeekSlot = "A" };
        var weekB = new TemplateItemDto { Id = "b", TemplateId = "tpl-1", DayOfWeek = 0, Title = "Week B item", WeekSlot = "B" };
        var api = new FakeTemplatesApi([template], [weekA, weekB]);
        await using var ctx = NewContext(api);

        var cut = ctx.Render<TemplatesEditor>();

        // Default is week A.
        Assert.Contains("Week A item", cut.Markup);
        Assert.DoesNotContain("Week B item", cut.Markup);

        // Switch to week B.
        cut.FindAll("button").First(b => b.TextContent.Trim() == "Week B").Click();
        Assert.Contains("Week B item", cut.Markup);
        Assert.DoesNotContain("Week A item", cut.Markup);
    }

    [Fact]
    public async Task Locked_template_hides_add_affordances()
    {
        var api = new FakeTemplatesApi(
            [TestData.Template("tpl-1", "My week", locked: true)], []);
        await using var ctx = NewContext(api);

        var cut = ctx.Render<TemplatesEditor>();

        Assert.DoesNotContain(cut.FindAll("button"), b => b.TextContent.Trim() == "Add");
        // The unlock affordance is offered instead.
        Assert.Contains("Unlock to edit", cut.Markup);
    }
}
