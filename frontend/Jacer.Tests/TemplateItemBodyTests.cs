using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Web;

namespace Jacer.Tests;

public class TemplateItemBodyTests
{
    private static BunitContext NewContext()
    {
        var ctx = new BunitContext();
        ctx.Services.AddMudServices();
        ctx.JSInterop.Mode = JSRuntimeMode.Loose;
        return ctx;
    }

    private static TemplateItemDto Item(string title, int minutes = 30, string? time = null) => new()
    {
        Id = "i1",
        TemplateId = "tpl-1",
        DayOfWeek = 0,
        Title = title,
        DurationMinutes = minutes,
        DefaultTime = time,
    };

    [Fact]
    public async Task Double_click_title_edits_in_place_and_saves()
    {
        await using var ctx = NewContext();
        TemplateTitleEdit? edit = null;
        var cut = ctx.Render<TemplateItemBody>(p => p
            .Add(c => c.Item, Item("Old"))
            .Add(c => c.OnEditTitle, EventCallback.Factory.Create<TemplateTitleEdit>(this, e => edit = e)));

        cut.Find(".template-item-body__title").DoubleClick();
        var input = cut.Find("input");
        input.Input("New");
        await input.KeyDownAsync(new KeyboardEventArgs { Key = "Enter" });

        Assert.NotNull(edit);
        Assert.Equal("i1", edit!.Value.ItemId);
        Assert.Equal("New", edit.Value.Title);
    }

    [Fact]
    public async Task Double_click_duration_edits_in_place_and_saves()
    {
        await using var ctx = NewContext();
        TemplateDurationEdit? edit = null;
        var cut = ctx.Render<TemplateItemBody>(p => p
            .Add(c => c.Item, Item("Task", minutes: 30))
            .Add(c => c.OnEditDuration, EventCallback.Factory.Create<TemplateDurationEdit>(this, e => edit = e)));

        cut.Find(".template-item-body__dur").DoubleClick();
        var input = cut.Find("input");
        input.Input("60");
        await input.KeyDownAsync(new KeyboardEventArgs { Key = "Enter" });

        Assert.NotNull(edit);
        Assert.Equal(60, edit!.Value.Minutes);
    }

    [Fact]
    public async Task Delete_invokes_OnDelete()
    {
        await using var ctx = NewContext();
        string? deleted = null;
        var cut = ctx.Render<TemplateItemBody>(p => p
            .Add(c => c.Item, Item("Bin me"))
            .Add(c => c.OnDelete, EventCallback.Factory.Create<string>(this, id => deleted = id)));

        cut.FindAll("button").First(b => b.GetAttribute("aria-label") == "Remove item").Click();
        Assert.Equal("i1", deleted);
    }

    [Fact]
    public async Task Non_interactive_body_is_not_editable()
    {
        await using var ctx = NewContext();
        var cut = ctx.Render<TemplateItemBody>(p => p
            .Add(c => c.Item, Item("Locked"))
            .Add(c => c.Interactive, false));

        // No delete affordance, and double-clicking the title does not open an input.
        Assert.DoesNotContain(cut.FindAll("button"), b => b.GetAttribute("aria-label") == "Remove item");
        cut.Find(".template-item-body__title").DoubleClick();
        Assert.Empty(cut.FindAll("input"));
    }
}
