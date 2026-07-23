using Microsoft.AspNetCore.Components.Web;
using Microsoft.Extensions.DependencyInjection;

namespace Jacer.Tests;

public class TemplatesEditorTests
{
    private static BunitContext NewContext(FakeTemplatesApi api)
    {
        var ctx = new BunitContext();
        ctx.Services.AddMudServices();
        ctx.Services.AddSingleton<ITemplatesApi>(api);
        ctx.Services.AddSingleton<ICategoriesApi>(new FakeCategoriesApi([]));
        ctx.JSInterop.Mode = JSRuntimeMode.Loose;
        return ctx;
    }

    private static FakeTemplatesApi ApiWithOneTemplate(params TemplateItemDto[] items) =>
        new([TestData.Template("tpl-1", "My week")], items);

    [Fact]
    public async Task Grid_renders_all_seven_weekdays()
    {
        var api = ApiWithOneTemplate();
        await using var ctx = NewContext(api);

        var cut = ctx.Render<TemplatesEditor>();

        foreach (var day in TimelineGrid.DayLabels)
        {
            Assert.Contains(day, cut.Markup);
        }
    }

    [Fact]
    public async Task Timed_item_renders_on_its_days_timeline()
    {
        var api = ApiWithOneTemplate(
            TestData.Item("i1", "tpl-1", dayOfWeek: 0, title: "Morning standup", time: "09:00"));
        await using var ctx = NewContext(api);

        var cut = ctx.Render<TemplatesEditor>();

        Assert.Contains("Morning standup", cut.Markup);
        Assert.Contains("09:00", cut.Markup);
    }

    [Fact]
    public async Task Clicking_add_reveals_an_untimed_input()
    {
        var api = ApiWithOneTemplate();
        await using var ctx = NewContext(api);
        var cut = ctx.Render<TemplatesEditor>();

        var addButtons = cut.FindAll("button").Where(b => b.TextContent.Contains("Add")).ToList();
        Assert.NotEmpty(addButtons);
        addButtons[0].Click();

        Assert.Contains("Tick-off task…", cut.Markup);
    }

    [Fact]
    public async Task Clicking_away_from_a_new_item_saves_it()
    {
        // The click-away bug: blur must SAVE the typed text, not discard it.
        var api = ApiWithOneTemplate();
        await using var ctx = NewContext(api);
        var cut = ctx.Render<TemplatesEditor>();

        cut.FindAll("button").First(b => b.TextContent.Contains("Add")).Click();
        var input = cut.Find("input[placeholder='Tick-off task…']");
        input.Input("Take medicine");
        await input.BlurAsync(new FocusEventArgs());

        Assert.Contains(api.CreatedItems, i => i.Title == "Take medicine" && i.DefaultTime is null);
    }

    [Fact]
    public async Task Added_item_is_untimed_no_forced_time_slot()
    {
        var api = ApiWithOneTemplate();
        await using var ctx = NewContext(api);
        var cut = ctx.Render<TemplatesEditor>();

        cut.FindAll("button").First(b => b.TextContent.Contains("Add")).Click();
        var input = cut.Find("input[placeholder='Tick-off task…']");
        input.Input("Stretch");
        await input.KeyDownAsync(new KeyboardEventArgs { Key = "Enter" });

        Assert.Contains(api.CreatedItems, i => i.Title == "Stretch");
        Assert.All(api.CreatedItems, i => Assert.Null(i.DefaultTime));
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

        Assert.Contains("Week A item", cut.Markup);
        Assert.DoesNotContain("Week B item", cut.Markup);

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
        Assert.Contains("Unlock to edit", cut.Markup);
    }
}
