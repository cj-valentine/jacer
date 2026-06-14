namespace Jacer.Tests;

public class TaskColumnTests
{
    private static BunitContext NewContext()
    {
        var ctx = new BunitContext();
        ctx.Services.AddMudServices();
        ctx.JSInterop.Mode = JSRuntimeMode.Loose;
        return ctx;
    }

    [Fact]
    public async Task Renders_column_label_and_cards()
    {
        await using var ctx = NewContext();
        var tasks = new[]
        {
            TestData.Task("Standup", TaskStatus.Today, 15),
            TestData.Task("Review PR", TaskStatus.Today, 30),
        };

        var cut = ctx.Render<TaskColumn>(p => p
            .Add(c => c.Status, TaskStatus.Today)
            .Add(c => c.Tasks, tasks));

        Assert.Contains("Today", cut.Markup);
        Assert.Contains("Standup", cut.Markup);
        Assert.Contains("Review PR", cut.Markup);
        Assert.DoesNotContain("No tasks", cut.Markup);
    }

    [Fact]
    public async Task Empty_column_shows_no_tasks()
    {
        await using var ctx = NewContext();

        var cut = ctx.Render<TaskColumn>(p => p
            .Add(c => c.Status, TaskStatus.Scheduled)
            .Add(c => c.Tasks, Array.Empty<TaskDto>()));

        Assert.Contains("Scheduled", cut.Markup);
        Assert.Contains("No tasks", cut.Markup);
    }
}
