;; artifact: nature_catalog
FILE data/nature.txt
# Source phenomena catalog
# format: code | description
# Derived algorithms live in data/algorithms.json
# Each code here MUST have a matching "phenomenon" entry there.

# --- stochastic search & diffusion ---
levy_flight | Heavy-tailed random walk; step lengths drawn from a power-law distribution, producing rare long excursions between clusters of short moves. Optimal search strategy for sparse, randomly distributed targets (cf. foraging albatross, T cells).
# BACKLOG (not yet derived): wiener | Continuous-time Brownian motion; increments are independent Gaussians with variance proportional to dt. The canonical null model for diffusive transport and noisy accumulation.

# --- synchronization & collective dynamics ---
kuramoto | Phase oscillators with all-to-all sinusoidal coupling; above a critical coupling strength a macroscopic mean field spontaneously synchronizes (fireflies, pacemaker cells, Josephson junctions).

# --- population & ecological dynamics ---
lotka_volterra | Coupled predator-prey ODEs; prey grow exponentially, predators consume prey at rate proportional to the product, predators decay without prey. Neutral cycles about a fixed point.
logistic | Density-dependent growth with carrying capacity K; growth is linear at small x and vanishes at x = K. The simplest model of resource-limited reproduction.
gompertz | Asymmetric sigmoid growth with exponentially decaying specific growth rate; used for tumor growth and mortality curves where decline is slower than rise.
allee | Positive density dependence at low abundance: growth is negative below a critical threshold A (mate-finding, cooperative defense) and logistic above it.
sir | Compartmental epidemic model (Susceptible-Infectious-Recovered) with mass-action transmission; gives the epidemic threshold R0 = beta/gamma.
sirs | SIR extended with waning immunity, so recovered individuals return to the susceptible pool; supports endemic steady states.
host_parasite | Coevolving host-parasite genotype frequencies under negative frequency-dependent selection; the classic Red Queen dynamic with no stable winner.
predator_prey_spatial | Spatially extended predator-prey with Holling-type functional response and diffusion; admits Turing instabilities that break spatial symmetry into patches.
bacterial_chemotaxis | Run-and-tumble motility biased by temporal gradient sensing; bacteria lengthen runs when moving up an attractant gradient.

# --- transport & continuum mechanics ---
fick | Linear constitutive law for diffusive flux: J = -D grad(c). The defining relation of molecular diffusion.
darcy | Empirical law for flow through porous media: velocity is proportional to the pressure gradient divided by viscosity.
poiseuille | Laminar viscous flow through a cylindrical pipe; volumetric flow scales with the fourth power of radius (Hagen-Poiseuille).
kirchhoff | Conservation of current at a network node: the algebraic sum of currents entering equals zero. Underpins circuit analysis and network flow.
fourier | Constitutive law of heat conduction: flux is proportional to the negative temperature gradient. Combined with energy conservation gives the heat equation.
nernst | Nernst-Planck equation for ion transport: diffusive flux plus drift of charged species in an electric field.
chemostat | Continuous culture with inflow of fresh medium and outflow of culture; microbial growth follows Monod kinetics, dilution sets steady-state density.
osmosis | Solvent flow across a semipermeable membrane driven by the osmotic pressure difference; van 't Hoff relation for dilute solutes.
diffusion_limited | Reaction at a boundary whose rate is set by how fast reactants diffuse to it; effective kinetics become first-order at low concentration (Smoluchowski / Rice).

# --- pattern formation & excitable media ---
gray_scott | Two-species reaction-diffusion system with cubic autocatalysis; produces spots, stripes, and self-replicating patterns. Standard model of morphogenesis.

# --- neural & learning dynamics ---
hebbian | Activity-dependent synaptic plasticity: weight change is proportional to the product of pre- and post-synaptic activity. The substrate of associative memory.

# --- criticality, chaos & information ---
# BACKLOG (not yet derived): percolation | Random occupation of lattice sites or bonds; a spanning cluster appears at a sharp threshold pc. Canonical model of connectivity and phase transitions.
# BACKLOG (not yet derived): sandpile | Abelian sandpile / self-organized criticality: slow driving plus threshold toppling drives the system to a scale-free avalanche distribution.
# BACKLOG (not yet derived): ising | Lattice spins with nearest-neighbor coupling; order-disorder transition at a critical temperature. The archetype of collective phase transitions.
# BACKLOG (not yet derived): logistic_map | Quadratic iterated map r*x*(1-x); period-doubling route to chaos as r increases. Minimal discrete model of deterministic chaos.
# BACKLOG (not yet derived): lyapunov | Largest Lyapunov exponent quantifies exponential divergence of nearby trajectories; positive value signals deterministic chaos.
# BACKLOG (not yet derived): entropy | Shannon/Gibbs entropy of a distribution; monotone increase under coarse-graining and the informational measure of uncertainty.
# BACKLOG (not yet derived): max_entropy | Maximum-entropy principle: among distributions consistent with constraints, choose the one with largest entropy (Jaynes).
# BACKLOG (not yet derived): renormalization | Coarse-graining plus rescaling that leaves the partition function invariant; yields universal exponents at critical points.
# BACKLOG (not yet derived): bifurcation | Qualitative change in attractor structure as a parameter crosses a critical value (saddle-node, Hopf, pitchfork).
# BACKLOG (not yet derived): hysteresis | Path-dependent state: the response depends on the direction of parameter sweep, giving a loop between forward and reverse transitions.
quorum_sensing | Density-dependent gene expression in bacteria: cells secrete autoinducers and switch phenotype only above a threshold population density.
# BACKLOG (not yet derived): evolutionary_game | Replicator dynamics for strategy frequencies under payoff matrix; Nash equilibria appear as rest points.
# BACKLOG (not yet derived): fitness_landscape | Genotype-phenotype map with a scalar fitness; adaptive walks climb to local peaks (Wright, Kauffman NK model).
# BACKLOG (not yet derived): neutral_drift | Allele frequency changes by random sampling alone; fixation probability equals initial frequency (Kimura).
# BACKLOG (not yet derived): mutation_selection | Balance between recurrent mutation and purifying selection; determines equilibrium allele frequency.
# BACKLOG (not yet derived): hox_gradient | Morphogen gradient read out by threshold-responsive genes to specify positional identity along an axis (Wolpert's French flag).
# BACKLOG (not yet derived): turing | Reaction-diffusion system where a homogeneous steady state is destabilized by differential diffusion, producing stationary spatial patterns.
# BACKLOG (not yet derived): morphogen | Diffusible signaling molecule whose concentration field carries positional information during development.
# BACKLOG (not yet derived): chemotaxis | Directed cell or organism migration up (or down) a chemical gradient; the general biased-random-walk mechanism.
# BACKLOG (not yet derived): phototaxis | Directed movement in response to light; used by motile algae and bacteria to optimize photosynthetic exposure.
# BACKLOG (not yet derived): gravitropism | Directional growth of plants in response to gravity; auxin redistribution bends shoots up and roots down.
# BACKLOG (not yet derived): circadian | Endogenous ~24h oscillator entrained by light; core is a delayed negative-feedback loop (PER/CRY in mammals).
# BACKLOG (not yet derived): hormesis | Biphasic dose-response: low-dose stimulation, high-dose inhibition. Common in toxins and radiation.
# BACKLOG (not yet derived): predator_pit | Low-density prey refuge where predation pressure is relaxed, stabilizing coexistence.
# BACKLOG (not yet derived): metapopulation | Network of local populations linked by migration; persistence depends on colonization-extinction balance (Levins).
# BACKLOG (not yet derived): island_biogeography | Species richness on an island reflects immigration and extinction rates as functions of area and isolation (MacArthur & Wilson).
# BACKLOG (not yet derived): niche_partitioning | Coexisting species divide limiting resources along one or more axes, reducing competition.
# BACKLOG (not yet derived): competition_exclusion | Two species competing for a single limiting resource cannot coexist indefinitely; the better competitor excludes the other (Gause).
# BACKLOG (not yet derived): mutualism | Interspecific interaction with net benefit to both partners; modeled by coupled logistic equations with positive cross-terms.
# BACKLOG (not yet derived): symbiosis | Long-term physical association between species; ranges from mutualism to parasitism along a continuum.
# BACKLOG (not yet derived): eusociality | Reproductive division of labor with overlapping generations and cooperative care of young (Hamilton's haplodiploidy, kin selection).
# BACKLOG (not yet derived): kin_selection | Hamilton's rule: altruism spreads when rB > C, where r is relatedness, B benefit to recipient, C cost to actor.
# BACKLOG (not yet derived): sexual_selection | Traits evolve because they increase mating success, sometimes against survival (Fisher runaway, Zahavi handicap).
# BACKLOG (not yet derived): signaling | Costly signals evolve to be honest when the cost is negatively correlated with quality (Zahavi, Grafen).
# BACKLOG (not yet derived): reciprocal_altruism | Cooperation sustained by repeated interaction and tit-for-tat-like strategies (Axelrod, Trivers).
# BACKLOG (not yet derived): collective_motion | Flocking, schooling, and swarming emerge from local alignment and attraction rules (Vicsek, Boids).
# BACKLOG (not yet derived): flocking | Aligned motion of self-propelled agents with local velocity matching; order-disorder transition at a critical noise level.
# BACKLOG (not yet derived): swarming | Dense, coordinated motion without global alignment; driven by local attraction and repulsion.
# BACKLOG (not yet derived): stigmergy | Indirect coordination through traces left in the environment (ant pheromone trails, termite mounds).
ant_colony | Foraging and task allocation via pheromone-mediated positive feedback; shortest paths emerge from reinforcement.
# BACKLOG (not yet derived): bee_foraging | Nectar collection with waggle-dance recruitment; colony-level allocation tracks profitability.
termite_mound | Distributed construction with no central controller; ventilation and thermal regulation via mound architecture.
# BACKLOG (not yet derived): coral_reef | Sessile colonial organisms building calcium carbonate structure; symbiosis with zooxanthellae drives primary production.
# BACKLOG (not yet derived): mycorrhiza | Symbiotic association between plant roots and fungi; trades soil nutrients for photosynthate.
# BACKLOG (not yet derived): lichen | Composite organism of fungus and alga/cyanobacterium; a model of obligate mutualism and desiccation tolerance.
# BACKLOG (not yet derived): biofilm | Surface-attached microbial community encased in extracellular matrix; exhibits emergent antibiotic tolerance and quorum sensing.

# --- added to close catalog/derived gap ---
albatross_forage | Transoceanic foraging of wandering albatross; empirically power-law flight-time distribution with exponent near -1.5, matching a Lévy-flight search.
all_or_none | Threshold all-or-none firing of an axon; responses below threshold decay passively, above threshold produce a fixed action potential (Bowditch 1871).
allostasis | Stability through change: physiological setpoints shift predictively ahead of anticipated demand rather than being held fixed (Sterling & Eyer 1988).
ant_quorum | Ants commit to a new nest site when the number of recruiters at a candidate exceeds a quorum; a distributed decision rule with positive feedback (Pratt 2002).
area_restricted | Area-restricted search: after a prey encounter, a forager increases turning rate and slows, concentrating effort locally before resuming long-range movement (Benhamou 2007).
bee_waggle | Honeybee waggle dance encodes direction and distance to a resource; recruits sample dancers and the colony allocates foragers by profitability (von Frisch 1967).
belousov_zhabotinsky | Oscillating chemical reaction (bromate-malonic acid catalyst) producing travelling colour waves; the canonical excitable medium (Field, Kőrös & Noyes 1972).
boids | Reynolds' three rules — separation, alignment, cohesion — produce lifelike flocking from purely local, agent-level interactions (Reynolds 1987).
brownian_search | Random search with independent Gaussian increments; optimal when targets are dense and randomly placed (Einstein 1905; Viswanathan 1999).
circadian_clock | Cell-autonomous ~24 h oscillator built on interlocked transcriptional-translational feedback loops (PER/CRY, CLOCK/BMAL1) in mammals.
cricket_chorus | Male crickets adjust calling to neighbours' rhythm; small phase leads bias the population toward synchronous chorusing (Greenfield 1994).
dla | Diffusion-limited aggregation: random-walking particles stick irreversibly on contact, yielding fractal clusters with dimension ≈ 1.71 in 2D (Witten & Sander 1981).
eden_growth | Stochastic surface growth where a random perimeter site is added each step; produces a rough interface with KPZ-like scaling (Eden 1961).
elephant_walk | Elephant movement shows memory-driven, directionally persistent paths rather than pure Brownian or Lévy walks (Moorcroft 2006).
firefly_sync | Pulse-coupled oscillators: each firefly flashes, then resets its internal phase; large populations spontaneously synchronize (Mirollo & Strogatz 1990).
fish_school | Schools form via edge-following and attraction to neighbours, giving polarized, cohesive groups with emergent startle waves (Hemelrijk 2015).
fitzhugh_nagumo | Two-variable reduction of the Hodgkin-Huxley model; a fast activator and slow inhibitor produce excitable spikes and relaxation oscillations (FitzHugh 1961).
gene_switch | Bistable toggle switch built from two mutually repressing genes; the classic synthetic-biology memory element (Gardner, Cantor & Collins 2000).
habituation | Repeated neutral stimuli produce a decrementing response; the simplest form of non-associative learning (Thompson & Spencer 1966).
hodgkin_huxley | Quantitative model of the action potential from voltage-gated Na+ and K+ conductances; the founding biophysical model of excitability (Hodgkin & Huxley 1952).
homeostasis | Negative-feedback regulation holds internal variables near setpoints (Cannon 1932); error signal drives corrective action.
immune_affinity | Clonal selection: lymphocytes whose receptors match an antigen proliferate and differentiate; affinity maturation sharpens the response (Burnet 1959).
levy_walk_2d | Two-dimensional Lévy walk: step lengths power-law distributed, direction isotropic; optimal random search for sparse targets (Viswanathan 1999).
lichen_edge | Slow boundary expansion of crustose lichens; radial growth rate is roughly constant, making lichens a dating tool (Watson 2014).
locust_swarm | Dense marching bands form because locusts cannibalize the individual in front; local repulsion plus forward attraction produce coherent motion (Buhl 2006).
murmuration_critical | Starling murmurations show scale-free correlations and maximal susceptibility — evidence the flock operates near a critical point (Cavagna 2010).
neuron_threshold | Leaky integrate-and-fire: membrane potential integrates input and emits a spike when it crosses threshold, then resets (Lapicque 1907).
persistent_walk | Correlated random walk: heading is autocorrelated across steps, interpolating between ballistic and diffusive motion (Kareiva 1983).
phase_transition | Order parameter changes qualitatively as a control parameter crosses a critical value; Ising spins are the canonical example (Onsager 1944).
self_avoiding_walk | Random walk on a lattice that never revisits a site; models polymer conformation and gives the Flory exponent ν ≈ 3/4 in 2D (Flory 1949).
sensitization | Strong or noxious stimuli amplify subsequent responses; the mirror of habituation in non-associative learning (Groves & Thompson 1970).
slime_mold | Physarum forages by reinforcing tubes that carry more flux and pruning the rest, solving shortest-path problems without a nervous system (Tero 2007).
starling_murmuration | Topological (not metric) interaction: each bird tracks a fixed number of nearest neighbours regardless of distance, giving scale-free flocks (Ballerini 2008).
stdp | Spike-timing-dependent plasticity: synapses strengthen when pre precedes post within tens of ms and weaken in the reverse order (Bi & Poo 1998).
tree_branching | L-system rewriting rules generate self-similar branching structures that match real tree architecture and light capture (Prusinkiewicz 1990).
turing_pattern | Reaction-diffusion with differential diffusivity destabilizes a uniform state into stationary spots or stripes; morphogen basis of animal markings (Turing 1952).
ENDFILE data/nature.txt
