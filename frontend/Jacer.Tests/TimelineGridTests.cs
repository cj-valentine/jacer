namespace Jacer.Tests;

public class TimelineGridTests
{
    [Theory]
    [InlineData("09:30", 570)]
    [InlineData("00:00", 0)]
    [InlineData("23:59", 1439)]
    [InlineData("6:05", 365)]
    public void MinutesFromHhMm_parses_valid_times(string input, int expected) =>
        Assert.Equal(expected, TimelineGrid.MinutesFromHhMm(input));

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("nonsense")]
    [InlineData("25:00")]
    [InlineData("10:70")]
    public void MinutesFromHhMm_returns_null_for_bad_input(string? input) =>
        Assert.Null(TimelineGrid.MinutesFromHhMm(input));

    [Theory]
    [InlineData(570, "09:30")]
    [InlineData(0, "00:00")]
    [InlineData(480, "08:00")]
    public void HhMmFromMinutes_formats(int minutes, string expected) =>
        Assert.Equal(expected, TimelineGrid.HhMmFromMinutes(minutes));

    [Fact]
    public void SlotCount_counts_slots_in_window()
    {
        Assert.Equal(32, TimelineGrid.SlotCount(6, 22, 30));   // 16h at 30-min
        Assert.Equal(48, TimelineGrid.SlotCount(0, 24, 30));
    }

    [Fact]
    public void SlotStartMinute_maps_slot_index_to_minutes()
    {
        Assert.Equal(6 * 60, TimelineGrid.SlotStartMinute(6, 0, 30));
        Assert.Equal(8 * 60, TimelineGrid.SlotStartMinute(6, 4, 30));
    }
}
