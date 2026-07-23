using MudBlazor;

namespace Jacer.Web;

/// <summary>
/// Crucible-style dark theme (Phase 3.5): a near-black charcoal base — not pure
/// black — with a single warm molten-amber accent used sparingly (primary
/// actions, the today marker). Muted category colours live on card edges, driven
/// by the backend palette. Calm and quiet, information-dense, low visual noise.
/// A first pass the owner will tune.
/// </summary>
public static class JacerTheme
{
    public static readonly MudTheme Instance = new()
    {
        PaletteDark = new PaletteDark
        {
            // The one warm accent.
            Primary = "#E27A3F",
            PrimaryContrastText = "#1A1712",
            Secondary = "#8A8F98",
            SecondaryContrastText = "#EDEEF0",

            // Charcoal base — a few steps off pure black, with cards lifted.
            Black = "#0F1013",
            Background = "#16171B",
            BackgroundGray = "#1E1F24",
            Surface = "#212328",
            AppbarBackground = "#1A1B1F",
            AppbarText = "#E6E7EA",
            DrawerBackground = "#1A1B1F",
            DrawerText = "#E6E7EA",

            // High-contrast, readable type.
            TextPrimary = "#E8E9EC",
            TextSecondary = "#A4A8B0",
            TextDisabled = "#6C7079",

            // Quiet structure.
            LinesDefault = "#2E3036",
            LinesInputs = "#3A3D44",
            Divider = "#2E3036",
            TableLines = "#2E3036",
            ActionDefault = "#A4A8B0",
            ActionDisabled = "#55585F",
            ActionDisabledBackground = "#2A2C31",

            // Status colours: muted, distinct from the amber accent.
            Success = "#6FA86F",
            Warning = "#C7952B",
            Error = "#C7594E",
            Info = "#5B7B9A",
        },
        LayoutProperties = new LayoutProperties
        {
            DefaultBorderRadius = "6px",
        },
    };
}
