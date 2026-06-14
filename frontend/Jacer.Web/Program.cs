using Jacer.ApiClient;
using Jacer.Web.Components;
using MudBlazor.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

builder.Services.AddMudServices();

// Typed client for the frozen FastAPI backend. Base URL is config-driven
// (appsettings: Jacer:ApiBaseUrl), defaulting to the local dev backend.
// The trailing slash matters so relative paths combine correctly.
var apiBaseUrl = builder.Configuration["Jacer:ApiBaseUrl"] ?? "http://localhost:8000";
if (!apiBaseUrl.EndsWith('/'))
{
    apiBaseUrl += "/";
}
builder.Services.AddHttpClient<ITasksApi, TasksApiClient>(client =>
{
    client.BaseAddress = new Uri(apiBaseUrl);
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}
app.UseStatusCodePagesWithReExecute("/not-found", createScopeForStatusCodePages: true);
app.UseHttpsRedirection();

app.UseAntiforgery();

app.MapStaticAssets();
app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();
