# Adapter assessment

The current Go verifier bridge invokes bounded JSON subprocess calls and keeps
the candidate outside trusted imports. That contract is insufficient for this
revision's actual behavior.

Observed hard dependencies include Docker Engine API/socket calls, Docker
Compose and Swarm lifecycle, nested Docker-in-Docker services, volume mounts,
filesystem ownership and symlink metadata, cloud and SSH/SFTP storage, GPG and
age binaries, SMTP/notification endpoints, cron and signal lifecycle, and
external hook processes. The upstream integration harness also pulls or loads
service images and uses credentials supplied through environment/config files.

A fake Docker or cloud implementation would not be faithful, while granting
the verifier host Docker access would violate the no-network and candidate
isolation boundaries. No deterministic child-side fixture covering this
surface is currently approved. The candidate is therefore blocked rather than
reduced to a misleading one-call API task.
