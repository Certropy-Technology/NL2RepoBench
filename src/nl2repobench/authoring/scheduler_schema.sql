-- Phase 1 SQLite scheduler schema.  This file is executed only by the typed
-- scheduler API; it deliberately contains no migration or live-service logic.
CREATE TABLE schema_meta (
  key TEXT PRIMARY KEY CHECK(length(key) BETWEEN 1 AND 128),
  value TEXT NOT NULL CHECK(length(value) <= 4096)
);

CREATE TABLE lanes (
  lane_id TEXT PRIMARY KEY,
  batch_id TEXT NOT NULL UNIQUE,
  language TEXT NOT NULL CHECK(language IN ('python','node','go')),
  kind TEXT NOT NULL CHECK(kind IN ('base','generated')),
  status TEXT NOT NULL CHECK(status IN ('planned','active','draining','closed','blocked')),
  queue_path TEXT NOT NULL, queue_sha256 TEXT NOT NULL,
  plan_path TEXT NOT NULL, plan_sha256 TEXT NOT NULL,
  state_path TEXT, state_sha256 TEXT,
  source_reports_json TEXT NOT NULL,
  fairness_rank INTEGER NOT NULL CHECK(fairness_rank >= 0),
  last_dispatch_seq INTEGER NOT NULL DEFAULT 0 CHECK(last_dispatch_seq >= 0),
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX lanes_schedule ON lanes(status, language, last_dispatch_seq, fairness_rank, lane_id);

CREATE TABLE candidate_identities (
  identity_digest TEXT PRIMARY KEY,
  language TEXT NOT NULL CHECK(language IN ('python','node','go')),
  package TEXT NOT NULL, upstream_url TEXT NOT NULL, source_kind TEXT NOT NULL,
  revision TEXT NOT NULL CHECK(length(revision) = 40),
  canonical_json TEXT NOT NULL, created_at TEXT NOT NULL
);

CREATE TABLE candidates (
  candidate_id TEXT NOT NULL,
  lane_id TEXT NOT NULL REFERENCES lanes(lane_id),
  identity_digest TEXT NOT NULL REFERENCES candidate_identities(identity_digest),
  input_ordinal INTEGER NOT NULL CHECK(input_ordinal >= 0),
  discovered_status TEXT NOT NULL CHECK(discovered_status IN ('candidate','needs-evidence','existing','rejected')),
  selection_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  PRIMARY KEY(candidate_id, lane_id), UNIQUE(lane_id, identity_digest)
);
CREATE INDEX candidates_lane ON candidates(lane_id, input_ordinal);

CREATE TABLE tasks (
  task_id TEXT PRIMARY KEY,
  candidate_id TEXT NOT NULL, lane_id TEXT NOT NULL, task_release TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN (
    'pending','claimed','preparing','authoring','handoff_ready','stale',
    'integrating','integration_retry','archiving','archive_retry','cleaning','cleanup_retry',
    'complete','blocked','excluded','cancelled')),
  attempt_limit INTEGER NOT NULL CHECK(attempt_limit BETWEEN 1 AND 100),
  authoring_attempts INTEGER NOT NULL DEFAULT 0 CHECK(authoring_attempts >= 0),
  retry_limit INTEGER NOT NULL CHECK(retry_limit BETWEEN 0 AND 100),
  retry_count INTEGER NOT NULL DEFAULT 0 CHECK(retry_count >= 0),
  release_count INTEGER NOT NULL DEFAULT 0 CHECK(release_count >= 0),
  release_limit INTEGER NOT NULL DEFAULT 3 CHECK(release_limit BETWEEN 0 AND 100),
  integration_attempts INTEGER NOT NULL DEFAULT 0 CHECK(integration_attempts >= 0),
  integration_retry_count INTEGER NOT NULL DEFAULT 0 CHECK(integration_retry_count >= 0),
  integration_retry_limit INTEGER NOT NULL DEFAULT 3 CHECK(integration_retry_limit BETWEEN 0 AND 100),
  archive_attempts INTEGER NOT NULL DEFAULT 0 CHECK(archive_attempts >= 0),
  archive_retry_count INTEGER NOT NULL DEFAULT 0 CHECK(archive_retry_count >= 0),
  archive_retry_limit INTEGER NOT NULL DEFAULT 3 CHECK(archive_retry_limit BETWEEN 0 AND 100),
  cleanup_attempts INTEGER NOT NULL DEFAULT 0 CHECK(cleanup_attempts >= 0),
  cleanup_retry_count INTEGER NOT NULL DEFAULT 0 CHECK(cleanup_retry_count >= 0),
  cleanup_retry_limit INTEGER NOT NULL DEFAULT 3 CHECK(cleanup_retry_limit BETWEEN 0 AND 100),
  next_retry_at TEXT, priority_until TEXT, input_ordinal INTEGER NOT NULL DEFAULT 0 CHECK(input_ordinal >= 0),
  last_failure_class TEXT, last_failure_reason TEXT,
  worktree_path TEXT, worktree_git_head TEXT, worktree_digest TEXT, source_digest TEXT,
  handoff_path TEXT, handoff_sha256 TEXT, terminal_reason TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  FOREIGN KEY(candidate_id, lane_id) REFERENCES candidates(candidate_id, lane_id),
  UNIQUE(candidate_id, lane_id, task_release),
  CHECK(authoring_attempts <= attempt_limit), CHECK(retry_count <= retry_limit),
  CHECK(release_count <= release_limit),
  CHECK((state NOT IN ('complete','blocked','excluded','cancelled')) OR terminal_reason IS NOT NULL)
);
CREATE UNIQUE INDEX tasks_one_live_release ON tasks(candidate_id, lane_id)
  WHERE state NOT IN ('complete','blocked','excluded','cancelled');
CREATE UNIQUE INDEX tasks_one_worktree ON tasks(worktree_path)
  WHERE worktree_path IS NOT NULL AND state NOT IN ('complete','blocked','excluded','cancelled');
CREATE INDEX tasks_claimable ON tasks(state, next_retry_at, lane_id, updated_at, task_id);

CREATE TABLE controllers (
  controller_id TEXT PRIMARY KEY, owner_uuid TEXT NOT NULL UNIQUE,
  role TEXT NOT NULL CHECK(role IN ('authoring_controller','supervisor','watcher','integration','archive')),
  lane_id TEXT REFERENCES lanes(lane_id), language TEXT CHECK(language IS NULL OR language IN ('python','node','go')),
  slot INTEGER, pid INTEGER NOT NULL CHECK(pid > 0),
  process_starttime_ticks INTEGER NOT NULL CHECK(process_starttime_ticks >= 0),
  boot_id TEXT NOT NULL, executable_digest TEXT NOT NULL, argv_digest TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('running','draining','stopped','lost','reconciled')),
  desired INTEGER NOT NULL CHECK(desired IN (0,1)), last_seen_at TEXT NOT NULL,
  stopped_at TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  UNIQUE(controller_id, owner_uuid),
  CHECK((role = 'authoring_controller' AND lane_id IS NOT NULL AND language IS NOT NULL AND slot IS NOT NULL AND slot >= 0)
     OR (role <> 'authoring_controller' AND lane_id IS NULL AND language IS NULL AND slot IS NULL))
);
CREATE UNIQUE INDEX controllers_live_slot ON controllers(lane_id, slot)
  WHERE role = 'authoring_controller' AND state IN ('running','draining');

CREATE TABLE controller_slot_reservations (
  reservation_id TEXT PRIMARY KEY, reservation_token TEXT NOT NULL UNIQUE,
  lane_id TEXT NOT NULL REFERENCES lanes(lane_id), language TEXT NOT NULL CHECK(language IN ('python','node','go')),
  slot INTEGER NOT NULL CHECK(slot >= 0), owner_uuid TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('reserved','activated','released','expired')),
  reserved_at TEXT NOT NULL, expires_at TEXT NOT NULL, controller_id TEXT REFERENCES controllers(controller_id),
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE UNIQUE INDEX slot_one_reserved ON controller_slot_reservations(lane_id, slot) WHERE state = 'reserved';

CREATE TABLE scheduler_leases (
  lease_id TEXT PRIMARY KEY,
  scope TEXT NOT NULL CHECK(scope IN ('supervisor','watcher','integration','archive')),
  owner_uuid TEXT NOT NULL, controller_id TEXT NOT NULL, generation INTEGER NOT NULL CHECK(generation >= 1),
  leased_at TEXT NOT NULL, heartbeat_at TEXT NOT NULL, lease_expires_at TEXT NOT NULL,
  active INTEGER NOT NULL CHECK(active IN (0,1)), released_at TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  UNIQUE(scope, generation), UNIQUE(controller_id, owner_uuid, lease_id),
  FOREIGN KEY(controller_id, owner_uuid) REFERENCES controllers(controller_id, owner_uuid)
);
CREATE UNIQUE INDEX lease_one_active ON scheduler_leases(scope) WHERE active = 1;

CREATE TABLE trials (
  trial_id TEXT PRIMARY KEY, trial_sequence INTEGER NOT NULL UNIQUE,
  task_id TEXT NOT NULL REFERENCES tasks(task_id), attempt_no INTEGER NOT NULL CHECK(attempt_no >= 1),
  retry_no INTEGER NOT NULL CHECK(retry_no >= 0), kind TEXT NOT NULL CHECK(kind IN ('authoring','discovery','integration','archive','cleanup','reconcile')),
  state TEXT NOT NULL CHECK(state IN ('created','running','succeeded','failed','released','timed_out','cancelled','stale')),
  owner_uuid TEXT, controller_id TEXT, launch_intent_at TEXT, child_pid INTEGER,
  child_starttime_ticks INTEGER, child_boot_id TEXT, started_at TEXT, finished_at TEXT,
  exit_code INTEGER, failure_class TEXT, failure_reason TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  UNIQUE(task_id, attempt_no, retry_no, kind),
  CHECK((state = 'running' AND started_at IS NOT NULL) OR state <> 'running'),
  CHECK(finished_at IS NULL OR started_at IS NOT NULL)
);

CREATE TABLE claims (
  claim_id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(task_id),
  trial_id TEXT NOT NULL UNIQUE REFERENCES trials(trial_id), owner_uuid TEXT NOT NULL, controller_id TEXT NOT NULL,
  lease_seconds INTEGER NOT NULL CHECK(lease_seconds BETWEEN 5 AND 86400),
  heartbeat_interval_seconds INTEGER NOT NULL CHECK(heartbeat_interval_seconds BETWEEN 5 AND 86400),
  leased_at TEXT NOT NULL, heartbeat_at TEXT NOT NULL, lease_expires_at TEXT NOT NULL,
  released_at TEXT, release_reason TEXT, generation INTEGER NOT NULL CHECK(generation >= 1),
  active INTEGER NOT NULL CHECK(active IN (0,1)), created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  UNIQUE(task_id, generation), FOREIGN KEY(controller_id, owner_uuid) REFERENCES controllers(controller_id, owner_uuid)
);
CREATE UNIQUE INDEX claim_one_active ON claims(task_id) WHERE active = 1;

-- Units prevent controller reservations from consuming active authoring claim capacity.
CREATE TABLE capacity_rows (
  capacity_unit TEXT NOT NULL CHECK(capacity_unit IN ('controller_slot','active_claim')),
  capacity_kind TEXT NOT NULL CHECK(capacity_kind IN ('global','controller','language','agent')),
  capacity_key TEXT NOT NULL, limit_count INTEGER NOT NULL CHECK(limit_count >= 0),
  used_count INTEGER NOT NULL CHECK(used_count >= 0),
  remaining_count INTEGER NOT NULL CHECK(remaining_count = limit_count - used_count AND remaining_count >= 0),
  config_version INTEGER, updated_at TEXT NOT NULL,
  PRIMARY KEY(capacity_unit, capacity_kind, capacity_key)
);
CREATE TABLE fairness_state (
  fairness_id INTEGER PRIMARY KEY CHECK(fairness_id = 1), next_language_index INTEGER NOT NULL CHECK(next_language_index BETWEEN 0 AND 2),
  dispatch_sequence INTEGER NOT NULL CHECK(dispatch_sequence >= 0), updated_at TEXT NOT NULL
);
CREATE TABLE runtime_config (
  config_version INTEGER PRIMARY KEY AUTOINCREMENT, enabled INTEGER NOT NULL CHECK(enabled IN (0,1)),
  max_total_controllers INTEGER NOT NULL DEFAULT 0 CHECK(max_total_controllers BETWEEN 0 AND 6),
  controller_concurrency INTEGER NOT NULL DEFAULT 0 CHECK(controller_concurrency BETWEEN 0 AND 4),
  max_integrations INTEGER NOT NULL DEFAULT 0 CHECK(max_integrations BETWEEN 0 AND 3),
  agent_limit INTEGER CHECK(agent_limit IS NULL OR agent_limit BETWEEN 0 AND 6),
  lease_seconds INTEGER NOT NULL CHECK(lease_seconds BETWEEN 5 AND 86400),
  heartbeat_interval_seconds INTEGER NOT NULL CHECK(heartbeat_interval_seconds BETWEEN 5 AND 86400),
  changed_by TEXT NOT NULL, changed_at TEXT NOT NULL, reason TEXT NOT NULL CHECK(length(reason) BETWEEN 1 AND 500),
  CHECK(heartbeat_interval_seconds < lease_seconds)
);
CREATE VIEW current_runtime_config AS SELECT * FROM runtime_config
  WHERE config_version = (SELECT max(config_version) FROM runtime_config);

CREATE TABLE resource_policy (
  policy_version INTEGER PRIMARY KEY AUTOINCREMENT,
  repository_min_free_bytes INTEGER NOT NULL CHECK(repository_min_free_bytes > 0),
  docker_min_free_bytes INTEGER NOT NULL CHECK(docker_min_free_bytes > 0),
  watcher_min_free_bytes INTEGER NOT NULL CHECK(watcher_min_free_bytes > 0),
  changed_by TEXT NOT NULL, changed_at TEXT NOT NULL,
  reason TEXT NOT NULL CHECK(length(reason) BETWEEN 1 AND 500)
);
CREATE VIEW current_resource_policy AS SELECT * FROM resource_policy
  WHERE policy_version = (SELECT max(policy_version) FROM resource_policy);

CREATE TABLE cutover_barrier (
  barrier_id INTEGER PRIMARY KEY CHECK(barrier_id = 1),
  cutover_id TEXT NOT NULL UNIQUE,
  manifest_sha256 TEXT NOT NULL CHECK(length(manifest_sha256) = 64 AND manifest_sha256 NOT GLOB '*[^0-9a-f]*'),
  state TEXT NOT NULL CHECK(state IN ('prepared','sealed')),
  rollback_allowed INTEGER NOT NULL CHECK(rollback_allowed IN (0,1)),
  prepared_at TEXT NOT NULL, sealed_at TEXT,
  first_effect_kind TEXT CHECK(first_effect_kind IS NULL OR first_effect_kind IN ('claim','integration','archive','cleanup')),
  first_effect_task_id TEXT REFERENCES tasks(task_id),
  CHECK((state='prepared' AND rollback_allowed=1 AND sealed_at IS NULL AND first_effect_kind IS NULL)
     OR (state='sealed' AND rollback_allowed=0 AND sealed_at IS NOT NULL AND first_effect_kind IS NOT NULL))
);

CREATE TABLE operation_receipts (
  receipt_id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(task_id),
  operation_kind TEXT NOT NULL CHECK(operation_kind IN ('integration','archive','cleanup')),
  operation_attempt INTEGER NOT NULL CHECK(operation_attempt >= 1), retry_no INTEGER NOT NULL CHECK(retry_no >= 0),
  idempotency_key TEXT NOT NULL UNIQUE, status TEXT NOT NULL CHECK(status IN ('started','committed','pushed','verified','applied','failed','collision')),
  source_digest TEXT, generated_digest TEXT, commit_sha TEXT, external_ref TEXT,
  manifest_key TEXT, manifest_sha256 TEXT, source_snapshot_sha256 TEXT,
  object_count INTEGER, byte_count INTEGER, evidence_path TEXT, evidence_sha256 TEXT,
  actor_scope TEXT, actor_lease_id TEXT, actor_generation INTEGER,
  actor_id TEXT, actor_owner_uuid TEXT, actor_pid INTEGER,
  actor_starttime_ticks INTEGER, actor_boot_id TEXT,
  failure_class TEXT, failure_reason TEXT, receipt_json TEXT NOT NULL DEFAULT '{}',
  started_at TEXT NOT NULL, finished_at TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  UNIQUE(task_id, operation_kind, operation_attempt, retry_no),
  CHECK(status <> 'verified' OR (operation_kind = 'archive' AND manifest_key IS NOT NULL AND manifest_sha256 IS NOT NULL
    AND source_snapshot_sha256 IS NOT NULL AND object_count > 0 AND byte_count > 0 AND evidence_sha256 IS NOT NULL)),
  CHECK(status <> 'applied' OR (operation_kind = 'cleanup' AND evidence_path IS NOT NULL AND evidence_sha256 IS NOT NULL)),
  CHECK(status <> 'pushed' OR (operation_kind = 'integration' AND length(commit_sha)=40 AND commit_sha NOT GLOB '*[^0-9a-f]*' AND external_ref IS NOT NULL)),
  CHECK(manifest_sha256 IS NULL OR (length(manifest_sha256)=64 AND manifest_sha256 NOT GLOB '*[^0-9a-f]*')),
  CHECK(source_snapshot_sha256 IS NULL OR (length(source_snapshot_sha256)=64 AND source_snapshot_sha256 NOT GLOB '*[^0-9a-f]*')),
  CHECK(evidence_sha256 IS NULL OR (length(evidence_sha256)=64 AND evidence_sha256 NOT GLOB '*[^0-9a-f]*')),
  CHECK(source_digest IS NULL OR (length(source_digest)=64 AND source_digest NOT GLOB '*[^0-9a-f]*')),
  CHECK(generated_digest IS NULL OR (length(generated_digest)=64 AND generated_digest NOT GLOB '*[^0-9a-f]*'))
  ,CHECK(actor_scope IS NULL OR actor_scope IN ('integration','archive'))
  ,CHECK(status NOT IN ('pushed','verified','applied') OR actor_lease_id IS NOT NULL)
);

CREATE TABLE events (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, occurred_at TEXT NOT NULL,
  actor_type TEXT NOT NULL, actor_id TEXT, task_id TEXT REFERENCES tasks(task_id), trial_id TEXT REFERENCES trials(trial_id),
  claim_id TEXT REFERENCES claims(claim_id), lane_id TEXT REFERENCES lanes(lane_id),
  payload_json TEXT NOT NULL CHECK(length(payload_json) <= 16384), redaction_version TEXT NOT NULL DEFAULT '1'
);
CREATE INDEX events_task ON events(task_id, event_id);
CREATE TABLE status_snapshots (
  snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT, observed_at TEXT NOT NULL, supervisor_id TEXT NOT NULL,
  supervisor_lease_id TEXT NOT NULL, supervisor_generation INTEGER NOT NULL,
  config_version INTEGER NOT NULL REFERENCES runtime_config(config_version), payload_json TEXT NOT NULL CHECK(length(payload_json) <= 262144),
  payload_sha256 TEXT NOT NULL
);
CREATE TABLE artifacts (
  artifact_id TEXT PRIMARY KEY, task_id TEXT REFERENCES tasks(task_id), trial_id TEXT REFERENCES trials(trial_id),
  kind TEXT NOT NULL, path TEXT NOT NULL, sha256 TEXT NOT NULL, size_bytes INTEGER NOT NULL CHECK(size_bytes >= 0),
  secret_scan_status TEXT NOT NULL CHECK(secret_scan_status IN ('passed','blocked','not-run')),
  created_at TEXT NOT NULL, UNIQUE(path, sha256)
);
CREATE TABLE legacy_actor_evidence (
  legacy_actor_id TEXT PRIMARY KEY, source_path TEXT NOT NULL, owner_text TEXT NOT NULL, pid_text TEXT,
  starttime_text TEXT, boot_id_text TEXT, batch_id TEXT, raw_sha256 TEXT NOT NULL,
  classification TEXT NOT NULL CHECK(classification IN ('historical-owner','orphan-owner','stale-owner')), imported_at TEXT NOT NULL
);
CREATE TABLE orphan_claim_evidence (
  orphan_claim_id TEXT PRIMARY KEY, source_path TEXT NOT NULL, candidate_id_text TEXT, package_text TEXT,
  owner_text TEXT, status_text TEXT, lease_text TEXT, attempts_text TEXT, raw_sha256 TEXT NOT NULL,
  classification TEXT NOT NULL CHECK(classification IN ('orphan-claim','malformed-claim','unmapped-claim')),
  reason TEXT NOT NULL, imported_at TEXT NOT NULL
);

CREATE TRIGGER task_terminal_insert_guard BEFORE INSERT ON tasks
WHEN NEW.state IN ('complete','blocked','excluded','cancelled')
BEGIN SELECT RAISE(ABORT, 'terminal task insert forbidden'); END;
CREATE TRIGGER task_transition_guard BEFORE UPDATE OF state ON tasks
WHEN NOT (
 (OLD.state='pending' AND NEW.state IN ('claimed','blocked','excluded','cancelled')) OR
 (OLD.state='claimed' AND NEW.state IN ('preparing','stale','pending','blocked','excluded','cancelled')) OR
 (OLD.state='preparing' AND NEW.state IN ('authoring','stale','pending','blocked','excluded','cancelled')) OR
 (OLD.state='authoring' AND NEW.state IN ('handoff_ready','stale','pending','blocked','excluded','cancelled')) OR
 (OLD.state='handoff_ready' AND NEW.state IN ('integrating','blocked','excluded','cancelled')) OR
 (OLD.state='stale' AND NEW.state IN ('pending','blocked','excluded','cancelled')) OR
 (OLD.state='integrating' AND NEW.state IN ('archiving','integration_retry','blocked','excluded','cancelled')) OR
 (OLD.state='integration_retry' AND NEW.state IN ('integrating','blocked','excluded','cancelled')) OR
 (OLD.state='archiving' AND NEW.state IN ('cleaning','archive_retry','blocked','excluded','cancelled')) OR
 (OLD.state='archive_retry' AND NEW.state IN ('archiving','blocked','excluded','cancelled')) OR
 (OLD.state='cleaning' AND NEW.state IN ('complete','cleanup_retry','blocked','excluded','cancelled')) OR
 (OLD.state='cleanup_retry' AND NEW.state IN ('cleaning','blocked','excluded','cancelled')) OR OLD.state=NEW.state
)
BEGIN SELECT RAISE(ABORT, 'invalid task transition'); END;
CREATE TRIGGER task_complete_guard BEFORE UPDATE OF state ON tasks
WHEN NEW.state='complete'
BEGIN
 SELECT CASE WHEN NEW.terminal_reason IS NULL OR length(trim(NEW.terminal_reason))=0 THEN RAISE(ABORT,'terminal reason required') END;
 SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM operation_receipts WHERE task_id=NEW.task_id AND operation_kind='integration' AND status='pushed') THEN RAISE(ABORT,'pushed integration required') END;
 SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM operation_receipts WHERE task_id=NEW.task_id AND operation_kind='archive' AND status='verified') THEN RAISE(ABORT,'verified archive required') END;
 SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM operation_receipts WHERE task_id=NEW.task_id AND operation_kind='cleanup' AND status='applied') THEN RAISE(ABORT,'cleanup evidence required') END;
END;
CREATE TRIGGER operation_stage_guard BEFORE UPDATE OF state ON tasks
WHEN NEW.state='archiving' OR NEW.state='cleaning'
BEGIN
 SELECT CASE WHEN NEW.state='archiving' AND NOT EXISTS(
   SELECT 1 FROM operation_receipts WHERE task_id=NEW.task_id AND operation_kind='integration' AND status='pushed'
 ) THEN RAISE(ABORT,'pushed integration required before archive') END;
 SELECT CASE WHEN NEW.state='cleaning' AND NOT EXISTS(
   SELECT 1 FROM operation_receipts WHERE task_id=NEW.task_id AND operation_kind='archive' AND status='verified'
 ) THEN RAISE(ABORT,'verified archive required before cleanup') END;
END;
CREATE TRIGGER event_context_guard BEFORE INSERT ON events
WHEN (NEW.trial_id IS NOT NULL AND (NEW.task_id IS NULL OR NOT EXISTS(SELECT 1 FROM trials WHERE trial_id=NEW.trial_id AND task_id=NEW.task_id)))
  OR (NEW.claim_id IS NOT NULL AND (NEW.task_id IS NULL OR NOT EXISTS(SELECT 1 FROM claims WHERE claim_id=NEW.claim_id AND task_id=NEW.task_id)))
  OR (NEW.lane_id IS NOT NULL AND NEW.task_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM tasks WHERE task_id=NEW.task_id AND lane_id=NEW.lane_id))
BEGIN SELECT RAISE(ABORT, 'event context mismatch'); END;
CREATE TRIGGER controller_language_guard BEFORE INSERT ON controllers
WHEN NEW.role='authoring_controller' AND NOT EXISTS(SELECT 1 FROM lanes WHERE lane_id=NEW.lane_id AND language=NEW.language)
BEGIN SELECT RAISE(ABORT, 'controller language mismatch'); END;
CREATE TRIGGER snapshot_fence_guard BEFORE INSERT ON status_snapshots
WHEN NOT EXISTS(SELECT 1 FROM scheduler_leases WHERE scope='supervisor' AND lease_id=NEW.supervisor_lease_id
  AND generation=NEW.supervisor_generation AND active=1 AND lease_expires_at>NEW.observed_at AND controller_id=NEW.supervisor_id)
BEGIN SELECT RAISE(ABORT, 'supervisor lease fence mismatch'); END;
