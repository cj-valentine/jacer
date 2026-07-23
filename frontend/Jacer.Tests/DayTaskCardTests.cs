using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Web;

namespace Jacer.Tests;

public class DayTaskCardTests
{
    private static BunitContext NewContext()
    {
        var ctx = new BunitContext();
        ctx.Services.AddMudServices();
        ctx.JSInterop.Mode = JSRuntimeMode.Loose;
        return ctx;
    }

    private static CategoryDto Category(string id, string name, string colour) =>
        new() { Id = id, Name = name, Colour = colour };

    [Fact]
    public async Task Renders_title_and_duration()
    {
        await using var ctx = NewContext();
        var cut = ctx.Render<DayTaskCard>(p => p.Add(c => c.Task, TestData.Task("Write report", TaskStatus.Backlog, 45)));

        Assert.Contains("Write report", cut.Markup);
        Assert.Contains("45 min", cut.Markup);
    }

    [Fact]
    public async Task Diverged_task_shows_the_dot_and_reset_action_plain_does_not()
    {
        await using var ctx = NewContext();

        var diverged = ctx.Render<DayTaskCard>(p => p.Add(c => c.Task, TestData.DivergedTask("Edited")));
        Assert.Single(diverged.FindAll("span.diverged-dot"));
        Assert.Contains(diverged.FindAll("button"), b => b.GetAttribute("aria-label") == "Reset to template");

        var plain = ctx.Render<DayTaskCard>(p => p.Add(c => c.Task, TestData.Task("Plain", TaskStatus.Today)));
        Assert.Empty(plain.FindAll("span.diverged-dot"));
        Assert.DoesNotContain(plain.FindAll("button"), b => b.GetAttribute("aria-label") == "Reset to template");
    }

    [Fact]
    public async Task Complete_button_invokes_OnComplete()
    {
        await using var ctx = NewContext();
        var task = TestData.Task("Approve", TaskStatus.Today);
        string? completed = null;

        var cut = ctx.Render<DayTaskCard>(p => p
            .Add(c => c.Task, task)
            .Add(c => c.OnComplete, EventCallback.Factory.Create<string>(this, id => completed = id)));

        cut.FindAll("button").First(b => b.GetAttribute("aria-label") == "Complete").Click();
        Assert.Equal(task.Id, completed);
    }

    [Fact]
    public async Task Delete_button_invokes_OnDelete()
    {
        await using var ctx = NewContext();
        var task = TestData.Task("Bin me", TaskStatus.Today);
        string? deleted = null;

        var cut = ctx.Render<DayTaskCard>(p => p
            .Add(c => c.Task, task)
            .Add(c => c.OnDelete, EventCallback.Factory.Create<string>(this, id => deleted = id)));

        cut.FindAll("button").First(b => b.GetAttribute("aria-label") == "Delete").Click();
        Assert.Equal(task.Id, deleted);
    }

    [Fact]
    public async Task Reset_action_invokes_OnReset()
    {
        await using var ctx = NewContext();
        var task = TestData.DivergedTask("Edited");
        string? resetId = null;

        var cut = ctx.Render<DayTaskCard>(p => p
            .Add(c => c.Task, task)
            .Add(c => c.OnReset, EventCallback.Factory.Create<string>(this, id => resetId = id)));

        cut.FindAll("button").First(b => b.GetAttribute("aria-label") == "Reset to template").Click();
        Assert.Equal(task.Id, resetId);
    }

    [Fact]
    public async Task Double_click_title_edits_in_place_and_Enter_saves()
    {
        await using var ctx = NewContext();
        var task = TestData.Task("Old title", TaskStatus.Backlog);
        TaskTitleEdit? edit = null;

        var cut = ctx.Render<DayTaskCard>(p => p
            .Add(c => c.Task, task)
            .Add(c => c.OnEditTitle, EventCallback.Factory.Create<TaskTitleEdit>(this, e => edit = e)));

        cut.Find(".day-task-card__title").DoubleClick();
        var input = cut.Find("input");
        input.Input("New title");
        await input.KeyDownAsync(new KeyboardEventArgs { Key = "Enter" });

        Assert.NotNull(edit);
        Assert.Equal(task.Id, edit!.Value.TaskId);
        Assert.Equal("New title", edit.Value.Title);
    }

    [Fact]
    public async Task Date_chip_shows_for_upcoming_cards()
    {
        await using var ctx = NewContext();
        var today = new DateTime(2026, 7, 24);
        var task = TestData.Task("Future", TaskStatus.Backlog) with { ScheduledDate = "2026-07-25" };

        var cut = ctx.Render<DayTaskCard>(p => p
            .Add(c => c.Task, task)
            .Add(c => c.Today, today)
            .Add(c => c.ShowDateChip, true));

        Assert.Contains("Tomorrow", cut.Markup);
    }

    [Fact]
    public async Task Category_paints_the_card_left_edge()
    {
        await using var ctx = NewContext();
        var task = TestData.Task("Filed", TaskStatus.Backlog) with { CategoryId = "c1" };

        var cut = ctx.Render<DayTaskCard>(p => p
            .Add(c => c.Task, task)
            .Add(c => c.Categories, new List<CategoryDto> { Category("c1", "Admin", "#5B7B9A") }));

        Assert.Contains("border-left: 4px solid #5B7B9A", cut.Find(".day-task-card").GetAttribute("style")!);
        Assert.Contains("Admin", cut.Markup);
    }

    [Fact]
    public async Task Dragging_the_card_reports_its_id()
    {
        await using var ctx = NewContext();
        var task = TestData.Task("Drag me", TaskStatus.Backlog);
        string? dragged = null;

        var cut = ctx.Render<DayTaskCard>(p => p
            .Add(c => c.Task, task)
            .Add(c => c.OnDragStart, EventCallback.Factory.Create<string>(this, id => dragged = id)));

        await cut.Find(".day-task-card").TriggerEventAsync("ondragstart", new DragEventArgs());
        Assert.Equal(task.Id, dragged);
    }
}
