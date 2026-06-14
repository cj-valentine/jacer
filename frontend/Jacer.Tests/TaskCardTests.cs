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
}
