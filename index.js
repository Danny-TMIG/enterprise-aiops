/**
 * @file index.js
 * @description Main Entrypoint for Enterprise AIOps Execution Broker
 */

import { runIngestionPipeline } from './ingress/pipeline.js';

export async function runPipeline() {
  try {
    const auditTrail = await runIngestionPipeline();
    console.log('\n=== Execution Completed Successfully ===');
    console.log(`Total Audit Events Recorded: ${auditTrail.length}`);
  } catch (err) {
    console.error('\n=== Pipeline Execution Failed ===');
    console.error(err.message);
    process.exit(1);
  }
}

runPipeline();
