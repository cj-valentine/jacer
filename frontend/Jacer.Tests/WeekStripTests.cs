using Microsoft.AspNetCore.Components;

namespace Jacer.Tests;

public class WeekStripTests
{
    private static BunitContext NewContext()
    {
        var ctx = new BunitContext();
        ctx.Services.AddMudServices();
        ctx.JSInterop.Mode = JSRuntimeMode.Loose;
        return ctx;
    }

    // Thu 2026-07-23 → Monday 2026-07-20.
    private static readonly DateTime Today = new(2026, 7, 23);
    private static readonly DateTime WeekStart = new(2026, 7, 20);

    [Fact]
    public void Renders_seven_days_with_today_and_selected_marked()
    {
        using var ctx = NewContext();
        var cut = ctx.Render<WeekStrip>(p => p
            .Add(c => c.WeekStart, WeekStart)
            .Add(c => c.SelectedDate, Today)
            .Add(c => c.Today, Today));

        Assert.Equal(7, cut.FindAll(".week-day").Count);
        Assert.Single(cut.FindAll(".week-day--today"));
        Assert.Single(cut.FindAll(".week-day--selected"));
        // The selected+today day is 23rd.
        Assert.Equal("2026-07-23", cut.Find(".week-day--today").GetAttribute("data-date"));
    }

    [Fact]
    public async Task Clicking_a_day_selects_it()
    {
        using var ctx = NewContext();
        DateTime? selected = null;
        var cut = ctx.Render<WeekStrip>(p => p
            .Add(c => c.WeekStart, WeekStart)
            .Add(c => c.SelectedDate, Today)
            .Add(c => c.Today, Today)
            .Add(c => c.OnSelectDay, EventCallback.Factory.Create<DateTime>(this, d => selected = d)));

        cut.Find("[data-date='2026-07-25']").Click();
        Assert.Equal(new DateTime(2026, 7, 25), selected);
    }

    [Fact]
    public async Task Chevrons_page_the_week()
    {
        using var ctx = NewContext();
        var prev = 0;
        var next = 0;
        var cut = ctx.Render<WeekStrip>(p => p
            .Add(c => c.WeekStart, WeekStart)
            .Add(c => c.SelectedDate, Today)
            .Add(c => c.Today, Today)
            .Add(c => c.OnPrevWeek, EventCallback.Factory.Create(this, () => prev++))
            .Add(c => c.OnNextWeek, EventCallback.Factory.Create(this, () => next++)));

        cut.FindAll("button").First(b => b.GetAttribute("aria-label") == "Previous week").Click();
        cut.FindAll("button").First(b => b.GetAttribute("aria-label") == "Next week").Click();

        Assert.Equal(1, prev);
        Assert.Equal(1, next);
    }

    [Theory]
    [InlineData("2026-07-23", "2026-07-20")]  // Thursday → Monday
    [InlineData("2026-07-20", "2026-07-20")]  // Monday → itself
    [InlineData("2026-07-26", "2026-07-20")]  // Sunday → that Monday
    public void MondayOf_returns_the_weeks_monday(string date, string expected) =>
        Assert.Equal(DateTime.Parse(expected), WeekStrip.MondayOf(DateTime.Parse(date)));
}
