// Disambiguate Jacer's task status from System.Threading.Tasks.TaskStatus,
// which ImplicitUsings pulls into every file in this project (.cs and .razor).
global using TaskStatus = Jacer.ApiClient.TaskStatus;
