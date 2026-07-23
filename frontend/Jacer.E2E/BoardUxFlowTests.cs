using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;
using NUnit.Framework;

namespace Jacer.E2E;

/// <summary>
/// End-to-end for the Phase 3.5 board interactions: schedule a backlog task by
/// dragging it onto the day timeline, resize it, then complete it. Native HTML5
/// drag is driven via dispatched dragstart/drop events (the board's handlers use
/// component state, not the DataTransfer payload), with waits for the Blazor
/// Server circuit to round-trip between steps.
/// Requires the frontend (JACER_WEB_URL) and backend running.
/// </summary>
[Parallelizable(ParallelScope.Self)]
[TestFixture]
public class BoardUxFlowTests : PageTest
{
    private static string BaseUrl =>
        Environment.GetEnvironmentVariable("JACER_WEB_URL") ?? "http://localhost:5099";

    [Test]
    public async Task Schedule_by_drag_then_resize_then_complete()
    {
        await Page.GotoAsync(BaseUrl, new() { WaitUntil = WaitUntilState.NetworkIdle });

        var quickAdd = Page.GetByPlaceholder("Add a task and press Enter…");
        await Expect(quickAdd).ToBeEnabledAsync(new() { Timeout = 15_000 });

        var title = $"Drag flow {Guid.NewGuid():N}";
        await quickAdd.FillAsync(title);
        await quickAdd.PressAsync("Enter");

        // The new backlog card.
        var card = Page.Locator(".day-task-card", new() { HasText = title });
        await Expect(card).ToBeVisibleAsync(new() { Timeout = 15_000 });

        // Drag it onto the 09:00 slot (index 6 in a 06:00 window). Native HTML5
        // drag needs a real DataTransfer for Blazor to build DragEventArgs, so
        // thread one through the dragstart → dragover → drop sequence.
        var dt1 = await Page.EvaluateHandleAsync("() => new DataTransfer()");
        await card.DispatchEventAsync("dragstart", new Dictionary<string, object> { ["dataTransfer"] = dt1 });
        await Page.WaitForTimeoutAsync(500);
        var slot = Page.Locator("[data-slot-index='6']").First;
        await slot.DispatchEventAsync("dragover", new Dictionary<string, object> { ["dataTransfer"] = dt1 });
        await slot.DispatchEventAsync("drop", new Dictionary<string, object> { ["dataTransfer"] = dt1 });

        // It now renders on the timeline as a positioned block.
        var timelineItem = Page.Locator(".timeline-item", new() { HasText = title });
        await Expect(timelineItem).ToBeVisibleAsync(new() { Timeout = 15_000 });

        var before = await timelineItem.BoundingBoxAsync();

        // Resize: drag the grip down to a later slot; the block grows taller.
        var dt2 = await Page.EvaluateHandleAsync("() => new DataTransfer()");
        await timelineItem.Locator(".timeline-item__resize")
            .DispatchEventAsync("dragstart", new Dictionary<string, object> { ["dataTransfer"] = dt2 });
        await Page.WaitForTimeoutAsync(500);
        var slot2 = Page.Locator("[data-slot-index='9']").First;
        await slot2.DispatchEventAsync("dragover", new Dictionary<string, object> { ["dataTransfer"] = dt2 });
        await slot2.DispatchEventAsync("drop", new Dictionary<string, object> { ["dataTransfer"] = dt2 });
        await Page.WaitForTimeoutAsync(600);

        var after = await timelineItem.BoundingBoxAsync();
        Assert.That(after!.Height, Is.GreaterThan(before!.Height),
            "resizing should make the timeline block taller");

        // Complete it — the card leaves the board.
        await timelineItem.GetByLabel("Complete").ClickAsync();
        await Expect(Page.GetByText(title)).ToHaveCountAsync(0, new() { Timeout = 15_000 });
    }
}
