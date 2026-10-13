// MQL — MongoDB Query Language examples for the defensive
// botnet C2 simulation. These are illustrative; no live MongoDB
// is required to run the Python simulation.
//
// Collections: bots, tasks, commands, results, kill_switch

// ── 1. insert a bot ────────────────────────────────────────────
db.bots.insertOne({
  _id: "b-001",
  hostname: "sim-host-01",
  os: "linux",
  arch: "x86_64",
  first_seen: new Date(),
  last_seen: new Date(),
  status: "idle",
  tags: ["sim", "lab"]
});

// ── 2. find all idle bots ──────────────────────────────────────
db.bots.find({ status: "idle" }, { _id: 1, hostname: 1 }).sort({ hostname: 1 });

// ── 3. queue a task for a bot ──────────────────────────────────
db.tasks.insertOne({
  bot_id: "b-001",
  kind: "heartbeat",
  payload: JSON.stringify({ interval: 30 }),
  created_at: new Date(),
  status: "queued"
});

// ── 4. mark a task dispatched ──────────────────────────────────
db.tasks.updateOne(
  { _id: ObjectId("000000000000000000000000") },
  { $set: { status: "sent", dispatched_at: new Date() } }
);

// ── 5. aggregate task counts per bot ───────────────────────────
db.tasks.aggregate([
  { $match: { status: { $in: ["queued", "sent"] } } },
  { $group: { _id: "$bot_id", pending: { $sum: 1 } } },
  { $sort: { pending: -1 } }
]);

// ── 6. join tasks with results ─────────────────────────────────
db.tasks.aggregate([
  { $lookup: {
      from: "results",
      localField: "_id",
      foreignField: "task_id",
      as: "results"
  }},
  { $match: { "results.0": { $exists: true } } },
  { $project: { bot_id: 1, kind: 1, result_count: { $size: "$results" } } }
]);

// ── 7. TTL index so results expire after 7 days ────────────────
db.results.createIndex({ received_at: 1 }, { expireAfterSeconds: 604800 });

// ── 8. kill switch — one document, always _id: 1 ───────────────
db.kill_switch.updateOne(
  { _id: 1 },
  { $set: { engaged: true, engaged_at: new Date(), reason: "exercise end" } },
  { upsert: true }
);

// ── 9. detect bots that have not checked in for 5 minutes ──────
const cutoff = new Date(Date.now() - 5 * 60 * 1000);
db.bots.find({ last_seen: { $lt: cutoff }, status: { $ne: "dead" } });

// ── 10. revoke every outstanding command ───────────────────────
db.commands.updateMany(
  { revoked: false },
  { $set: { revoked: true } }
);
