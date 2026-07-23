global using Bunit;
global using Jacer.ApiClient;
global using Jacer.Components;
global using Microsoft.Extensions.DependencyInjection;
global using MudBlazor.Services;

// Xunit is already a global using via the csproj <Using> item.
// Disambiguate Jacer's task status from System.Threading.Tasks.TaskStatus.
global using TaskStatus = Jacer.ApiClient.TaskStatus;
