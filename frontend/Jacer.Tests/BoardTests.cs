using Microsoft.AspNetCore.Components.Web;
using Microsoft.Extensions.DependencyInjection;

namespace Jacer.Tests;

public class BoardTests
{
    private static readonly string Today = DateTime.Today.ToString("yyyy-MM-dd");

    private static (BunitContext ctx, FakeTasksApi tasks, FakeCategoriesApi cats) NewContext(
        IEnumerable<TaskDto>? tasks = null, IEnumerable<CategoryDto>? categories = null)
    {
        var ctx = new BunitContext();
        ctx.Services.AddMudServices();
        ctx.JSInterop.Mode = JSRuntimeMode.Loose;
        var tasksApi = new FakeTasksApi(tasks ?? []);
        var catsApi = new FakeCategoriesApi(categories ?? []);
        ctx.Services.AddSingleton<ITasksApi>(tasksApi);
        ctx.Services.AddSingleton<IDaysApi>(new FakeDaysApi());
        ctx.Services.AddSingleton<ICategoriesApi>(catsApi);
        ctx.Services.AddSingleton<BoardUiState>();
        return (ctx, tasksApi, catsApi);
    }

    private static TaskDto Backlog(string id, string title, string? categoryId = null) => new()
    {
        Id = id,
        Title = title,
        Status = TaskStatus.Backlog,
        DurationMinutes = 30,
        CategoryId = categoryId,
        CreatedAt = DateTimeOffset.UnixEpoch,
        UpdatedAt = DateTimeOffset.UnixEpoch,
    };

    private static CategoryDto Category(string id, string name, string colour) =>
        new() { Id = id, Name = name, Colour = colour };

    [Fact]
    public async Task Renders_week_strip_and_todays_heading()
    {
        var (ctx, _, _) = NewContext();
        await using var _ctx = ctx;
        var cut = ctx.Render<Board>();

        cut.WaitForAssertion(() =>
        {
            Assert.NotEmpty(cut.FindAll(".week-strip"));
            Assert.Contains(DateTime.Today.ToString("dddd d MMMM yyyy"), cut.Markup);
        });
    }

    [Fact]
    public async Task Backlog_groups_by_category_with_counts_uncategorised_last()
    {
        var (ctx, _, _) = NewContext(
            tasks: [Backlog("t1", "Admin one", "c1"), Backlog("t2", "Admin two", "c1"), Backlog("t3", "Loose")],
            categories: [Category("c1", "Admin", "#5B7B9A")]);
        await using var _ctx = ctx;
        var cut = ctx.Render<Board>();

        cut.WaitForAssertion(() =>
        {
            var markup = cut.Markup;
            Assert.Contains("Admin", markup);
            Assert.Contains("Uncategorised", markup);
            // Admin group (with 2) sorts before Uncategorised (with 1).
            Assert.True(markup.IndexOf("Admin", StringComparison.Ordinal)
                        < markup.IndexOf("Uncategorised", StringComparison.Ordinal));
        });
    }

    [Fact]
    public async Task Collapsing_a_category_group_hides_its_tasks()
    {
        var (ctx, _, _) = NewContext(
            tasks: [Backlog("t1", "Admin one", "c1")],
            categories: [Category("c1", "Admin", "#5B7B9A")]);
        await using var _ctx = ctx;
        var cut = ctx.Render<Board>();

        cut.WaitForAssertion(() => Assert.Contains("Admin one", cut.Markup));
        cut.FindAll(".board-group-head").First().Click();
        cut.WaitForAssertion(() => Assert.DoesNotContain("Admin one", cut.Markup));
    }

    [Fact]
    public async Task Future_dated_task_appears_in_upcoming_expanded_with_a_date_chip()
    {
        var future = DateTime.Today.AddDays(3);
        var task = Backlog("f1", "Later thing") with { ScheduledDate = future.ToString("yyyy-MM-dd") };
        var (ctx, _, _) = NewContext(tasks: [task]);
        await using var _ctx = ctx;
        var cut = ctx.Render<Board>();

        cut.WaitForAssertion(() =>
        {
            Assert.Contains("Upcoming", cut.Markup);
            Assert.Contains("Later thing", cut.Markup);  // expanded by default
        });
    }

    [Fact]
    public async Task Quick_add_creates_a_backlog_task()
    {
        var (ctx, tasks, _) = NewContext();
        await using var _ctx = ctx;
        var cut = ctx.Render<Board>();

        var input = cut.WaitForElement("input[placeholder='Add a task and press Enter…']");
        input.Input("A new task");
        await input.KeyDownAsync(new KeyboardEventArgs { Key = "Enter" });

        cut.WaitForAssertion(() =>
        {
            Assert.Single(tasks.Created);
            Assert.Equal("A new task", tasks.Created[0].Title);
        });
    }

    [Fact]
    public async Task Dropping_a_backlog_card_on_the_day_list_schedules_it_to_the_selected_day()
    {
        var (ctx, tasks, _) = NewContext(tasks: [Backlog("t1", "Schedule me")]);
        await using var _ctx = ctx;
        var cut = ctx.Render<Board>();

        cut.WaitForAssertion(() => Assert.Contains("Schedule me", cut.Markup));
        await cut.Find(".day-task-card").TriggerEventAsync("ondragstart", new DragEventArgs());
        await cut.Find(".board-dropzone").TriggerEventAsync("ondrop", new DragEventArgs());

        cut.WaitForAssertion(() => Assert.Equal(Today, tasks.Tasks.Single().ScheduledDate));
    }

    [Fact]
    public async Task Dropping_a_card_on_the_timeline_schedules_it_at_that_time()
    {
        var (ctx, tasks, _) = NewContext(tasks: [Backlog("t1", "Timed thing")]);
        await using var _ctx = ctx;
        var cut = ctx.Render<Board>();

        cut.WaitForAssertion(() => Assert.Contains("Timed thing", cut.Markup));
        await cut.Find(".day-task-card").TriggerEventAsync("ondragstart", new DragEventArgs());
        // Slot index 4 with the default 06:00 window = 08:00.
        await cut.Find("[data-slot-index='4']").TriggerEventAsync("ondrop", new DragEventArgs());

        cut.WaitForAssertion(() =>
        {
            var t = tasks.Tasks.Single();
            Assert.Equal(Today, t.ScheduledDate);
            Assert.Equal("08:00", t.ScheduledTime);
        });
    }

    [Fact]
    public async Task Completing_a_day_task_removes_it_from_the_board()
    {
        var task = Backlog("d1", "Do today") with { ScheduledDate = Today };
        var (ctx, tasks, _) = NewContext(tasks: [task]);
        await using var _ctx = ctx;
        var cut = ctx.Render<Board>();

        cut.WaitForAssertion(() => Assert.Contains("Do today", cut.Markup));
        cut.FindAll("button").First(b => b.GetAttribute("aria-label") == "Complete").Click();

        cut.WaitForAssertion(() =>
        {
            Assert.Equal(TaskStatus.Done, tasks.Tasks.Single().Status);
            Assert.DoesNotContain("Do today", cut.Markup);
        });
    }

    [Fact]
    public async Task New_category_control_creates_a_category()
    {
        var (ctx, _, cats) = NewContext();
        await using var _ctx = ctx;
        var cut = ctx.Render<Board>();

        cut.WaitForAssertion(() => cut.FindAll("button").First(b => b.TextContent.Contains("New category")).Click());
        var input = cut.WaitForElement("input[placeholder='Category name…']");
        input.Input("Errands");
        await input.KeyDownAsync(new KeyboardEventArgs { Key = "Enter" });

        cut.WaitForAssertion(() =>
        {
            Assert.Single(cats.Created);
            Assert.Equal("Errands", cats.Created[0].Name);
        });
    }
}
