using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Web;

namespace Jacer.Tests;

public class DayTimelineTests
{
    private static BunitContext NewContext()
    {
        var ctx = new BunitContext();
        ctx.Services.AddMudServices();
        ctx.JSInterop.Mode = JSRuntimeMode.Loose;
        return ctx;
    }

    private static TimelineItem Item(string id, int startMinute, int duration, string? colour = null) =>
        new() { Id = id, Title = $"Item {id}", StartMinute = startMinute, DurationMinutes = duration, Colour = colour };

    [Fact]
    public void Renders_one_drop_slot_per_increment_in_the_window()
    {
        using var ctx = NewContext();
        var cut = ctx.Render<DayTimeline>(p => p
            .Add(c => c.StartHour, 6)
            .Add(c => c.EndHour, 22)
            .Add(c => c.SlotMinutes, 30));

        Assert.Equal(32, cut.FindAll(".timeline-slot").Count);
    }

    [Fact]
    public void Item_block_is_sized_proportional_to_duration_and_positioned_by_start()
    {
        using var ctx = NewContext();
        // Window starts 06:00; item at 07:00 for 60 min. RowHeightPx=20, slot=30.
        var cut = ctx.Render<DayTimeline>(p => p
            .Add(c => c.StartHour, 6)
            .Add(c => c.RowHeightPx, 20)
            .Add(c => c.Items, new List<TimelineItem> { Item("a", 7 * 60, 60) }));

        var block = cut.Find(".timeline-item");
        var style = block.GetAttribute("style")!;
        Assert.Contains("top: 40px", style);       // 60 min offset = 2 slots * 20px
        Assert.Contains("height: 40px", style);     // 60 min = 2 slots * 20px
    }

    [Fact]
    public void Category_colour_paints_the_left_edge()
    {
        using var ctx = NewContext();
        var cut = ctx.Render<DayTimeline>(p => p
            .Add(c => c.Items, new List<TimelineItem> { Item("a", 8 * 60, 30, "#5B7B9A") }));

        Assert.Contains("border-left-color: #5B7B9A", cut.Find(".timeline-item").GetAttribute("style")!);
    }

    [Fact]
    public async Task Dragging_an_item_onto_a_slot_moves_it_to_that_start_time()
    {
        using var ctx = NewContext();
        TimelineMove? captured = null;
        var cut = ctx.Render<DayTimeline>(p => p
            .Add(c => c.StartHour, 6)
            .Add(c => c.Items, new List<TimelineItem> { Item("a", 6 * 60, 30) })
            .Add(c => c.OnMove, EventCallback.Factory.Create<TimelineMove>(this, m => captured = m)));

        await cut.Find(".timeline-item").TriggerEventAsync("ondragstart", new DragEventArgs());
        // Slot index 4 in a 06:00 window = 08:00.
        await cut.Find("[data-slot-index='4']").TriggerEventAsync("ondrop", new DragEventArgs());

        Assert.NotNull(captured);
        Assert.Equal("a", captured!.Value.ItemId);
        Assert.Equal(8 * 60, captured.Value.StartMinute);
    }

    [Fact]
    public async Task Dragging_the_resize_grip_onto_a_slot_resizes_to_that_slot_end()
    {
        using var ctx = NewContext();
        TimelineResize? captured = null;
        var cut = ctx.Render<DayTimeline>(p => p
            .Add(c => c.StartHour, 6)
            .Add(c => c.Items, new List<TimelineItem> { Item("a", 6 * 60, 30) })
            .Add(c => c.OnResize, EventCallback.Factory.Create<TimelineResize>(this, r => captured = r)));

        await cut.Find(".timeline-item__resize").TriggerEventAsync("ondragstart", new DragEventArgs());
        // Drop on slot index 3 (06:00 + 3*30 = 07:30); item starts 06:00, so it
        // now runs through the end of that slot = 08:00 → 120 min.
        await cut.Find("[data-slot-index='3']").TriggerEventAsync("ondrop", new DragEventArgs());

        Assert.NotNull(captured);
        Assert.Equal("a", captured!.Value.ItemId);
        Assert.Equal(120, captured.Value.DurationMinutes);
    }

    [Fact]
    public void Non_interactive_timeline_has_no_resize_grip_and_is_not_draggable()
    {
        using var ctx = NewContext();
        var cut = ctx.Render<DayTimeline>(p => p
            .Add(c => c.Interactive, false)
            .Add(c => c.Items, new List<TimelineItem> { Item("a", 8 * 60, 30) }));

        Assert.Empty(cut.FindAll(".timeline-item__resize"));
        Assert.Equal("false", cut.Find(".timeline-item").GetAttribute("draggable"));
    }

    [Fact]
    public void ItemContent_overrides_the_default_body()
    {
        using var ctx = NewContext();
        var cut = ctx.Render<DayTimeline>(p => p
            .Add(c => c.Items, new List<TimelineItem> { Item("a", 8 * 60, 30) })
            .Add(c => c.ItemContent, (RenderFragment<TimelineItem>)(item => builder =>
            {
                builder.OpenElement(0, "span");
                builder.AddAttribute(1, "class", "custom-body");
                builder.AddContent(2, $"custom:{item.Id}");
                builder.CloseElement();
            })));

        Assert.Contains("custom:a", cut.Find(".custom-body").TextContent);
    }
}
