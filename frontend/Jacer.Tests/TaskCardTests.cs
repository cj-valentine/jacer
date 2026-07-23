using Microsoft.AspNetCore.Components;

namespace Jacer.Tests;

public class TaskCardTests
{
    private static BunitContext NewContext()
    {
        var ctx = new BunitContext();
        ctx.Services.AddMudServices();
        ctx.JSInterop.Mode = JSRuntimeMode.Loose;
        return ctx;
    }

    [Fact]
    public async Task Renders_title_and_duration()
    {
        await using var ctx = NewContext();
        var task = TestData.Task("Write report", TaskStatus.Backlog, 45);

        var cut = ctx.Render<TaskCard>(p => p
            .Add(c => c.Task, task)
            .Add(c => c.MoveTargets, BoardColumns.MoveTargetsFor(TaskStatus.Backlog)));

        Assert.Contains("Write report", cut.Markup);
        Assert.Contains("45 min", cut.Markup);
    }

    [Fact]
    public async Task Renders_a_move_button_for_each_other_column()
    {
        await using var ctx = NewContext();
        var task = TestData.Task("Triage", TaskStatus.Backlog);

        var cut = ctx.Render<TaskCard>(p => p
            .Add(c => c.Task, task)
            .Add(c => c.MoveTargets, BoardColumns.MoveTargetsFor(TaskStatus.Backlog)));

        var labels = cut.FindAll("button").Select(b => b.TextContent.Trim()).ToList();
        Assert.Contains(labels, l => l.Contains("Today"));
        Assert.Contains(labels, l => l.Contains("Scheduled"));
        Assert.DoesNotContain(labels, l => l.Contains("Backlog"));
    }

    [Fact]
    public async Task Move_button_invokes_OnMove_with_task_id_and_target()
    {
        await using var ctx = NewContext();
        var task = TestData.Task("Approve", TaskStatus.Backlog);
        TaskMove? captured = null;

        var cut = ctx.Render<TaskCard>(p => p
            .Add(c => c.Task, task)
            .Add(c => c.MoveTargets, BoardColumns.MoveTargetsFor(TaskStatus.Backlog))
            .Add(c => c.OnMove, EventCallback.Factory.Create<TaskMove>(this, m => captured = m)));

        cut.FindAll("button").First(b => b.TextContent.Contains("Today")).Click();

        Assert.NotNull(captured);
        Assert.Equal(task.Id, captured!.Value.TaskId);
        Assert.Equal(TaskStatus.Today, captured.Value.Target);
    }

    [Fact]
    public async Task Diverged_task_shows_the_diverged_dot()
    {
        await using var ctx = NewContext();

        var diverged = ctx.Render<TaskCard>(p => p.Add(c => c.Task, TestData.DivergedTask("Edited")));
        Assert.Single(diverged.FindAll("span.diverged-dot"));

        var plain = ctx.Render<TaskCard>(p => p.Add(c => c.Task, TestData.Task("Plain", TaskStatus.Today)));
        Assert.Empty(plain.FindAll("span.diverged-dot"));
    }

    [Fact]
    public async Task Bump_menu_items_invoke_OnBump_with_the_right_offset()
    {
        await using var ctx = NewContext();
        var task = TestData.Task("Reschedule", TaskStatus.Today);
        TaskBump? captured = null;

        var cut = ctx.Render<TaskCard>(p => p
            .Add(c => c.Task, task)
            .Add(c => c.OnBump, EventCallback.Factory.Create<TaskBump>(this, b => captured = b)));

        cut.FindAll("button").First(b => b.TextContent.Contains("Next week")).Click();

        Assert.NotNull(captured);
        Assert.Equal(task.Id, captured!.Value.TaskId);
        Assert.Equal(7, captured.Value.DaysAhead);
    }

    [Fact]
    public async Task Reset_action_only_shows_for_diverged_tasks_and_invokes_OnReset()
    {
        await using var ctx = NewContext();
        string? resetId = null;

        // A plain (non-diverged) task shows no reset action.
        var plain = ctx.Render<TaskCard>(p => p.Add(c => c.Task, TestData.Task("Plain", TaskStatus.Today)));
        Assert.DoesNotContain(plain.FindAll("button"), b => b.TextContent.Contains("Reset to template"));

        var task = TestData.DivergedTask("Edited");
        var cut = ctx.Render<TaskCard>(p => p
            .Add(c => c.Task, task)
            .Add(c => c.OnReset, EventCallback.Factory.Create<string>(this, id => resetId = id)));

        cut.FindAll("button").First(b => b.TextContent.Contains("Reset to template")).Click();

        Assert.Equal(task.Id, resetId);
    }
}
