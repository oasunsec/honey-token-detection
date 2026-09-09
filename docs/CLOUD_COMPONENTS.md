# Cloud components

| Change | Result |
| --- | --- |
| Build the receiver | The existing Dockerfile is built through Azure Container Registry. |
| Run the receiver | Container Apps provides public HTTPS callbacks. Management and docs routes return 404. |
| Save cloud events | Table Storage saves callback events and delivery results. |
| Use managed identity | The app uses scoped permissions for the registry, Table Storage, and DCR. |
| Send events to Sentinel | A redacted event is sent through a Direct DCR to `CanaryHit_CL`. |
| Keep source data simple | Forwarded headers are ignored, so the source is the direct connection peer. |
| Mark requests | Scanner-like User-Agents are Medium; other first hits use the token severity; repeats use the token and User-Agent. |
| Create detections | One rule handles High or Critical first hits and another handles Medium scanner first hits. Repeats are excluded. |
| Clean up | The teardown script requires `-Confirm`. It was not run during the recorded work. |

[Deployment](../AZURE_DEPLOYMENT.md) - [Architecture](../ARCHITECTURE.md)
