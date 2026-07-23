namespace Jacer.Tests;

public class TimeBandsTests
{
    [Theory]
    [InlineData("06:00", TimeBand.Morning)]
    [InlineData("09:00", TimeBand.Morning)]
    [InlineData("11:59", TimeBand.Morning)]
    [InlineData("12:00", TimeBand.Afternoon)]
    [InlineData("16:59", TimeBand.Afternoon)]
    [InlineData("17:00", TimeBand.Evening)]
    [InlineData("23:30", TimeBand.Evening)]
    public void BandOf_maps_times_to_bands(string time, TimeBand expected) =>
        Assert.Equal(expected, TimeBands.BandOf(time));

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("not-a-time")]
    public void BandOf_treats_missing_or_bad_time_as_anytime(string? time) =>
        Assert.Equal(TimeBand.Anytime, TimeBands.BandOf(time));

    [Fact]
    public void DefaultTimeFor_anytime_is_null()
    {
        Assert.Null(TimeBands.DefaultTimeFor(TimeBand.Anytime));
        Assert.Equal("09:00", TimeBands.DefaultTimeFor(TimeBand.Morning));
        Assert.Equal("13:00", TimeBands.DefaultTimeFor(TimeBand.Afternoon));
        Assert.Equal("18:00", TimeBands.DefaultTimeFor(TimeBand.Evening));
    }

    [Fact]
    public void Round_trip_default_time_lands_in_its_own_band()
    {
        foreach (var band in TimeBands.Order)
        {
            Assert.Equal(band, TimeBands.BandOf(TimeBands.DefaultTimeFor(band)));
        }
    }
}
