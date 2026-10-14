# Artifact: algorithms

Path: `data/algorithms.json`

```
{
  "schema_version": "1.0",
  "derived_from": "data/nature.txt",
  "algorithms": [
    {
      "phenomenon": "levy_flight",
      "algorithm": "levy_flight_step",
      "params": [
        "alpha",
        "scale"
      ],
      "math": "x_{n+1} = x_n + s * L(alpha), s ~ heavy-tailed",
      "reference": "Viswanathan 1999, Nature 401:911"
    },
    {
      "phenomenon": "brownian_search",
      "algorithm": "wiener_step",
      "params": [
        "sigma",
        "dt"
      ],
      "math": "x_{n+1} = x_n + N(0, sigma^2 dt)",
      "reference": "Einstein 1905, Ann. Phys. 17:549"
    },
    {
      "phenomenon": "area_restricted",
      "algorithm": "area_restricted_search",
      "params": [
        "step",
        "radius"
      ],
      "math": "long steps + return-to-area kernel",
      "reference": "Benhamou 2007, Ecology 88:1962"
    },
    {
      "phenomenon": "albatross_forage",
      "algorithm": "levy_with_gradient",
      "params": [
        "alpha",
        "gradient_weight"
      ],
      "math": "levy step + k * grad(odor(x))",
      "reference": "Viswanathan 1996, Nature 381:413"
    },
    {
      "phenomenon": "bee_waggle",
      "algorithm": "waggle_average",
      "params": [
        "n_dancers",
        "noise"
      ],
      "math": "hive_vector = mean(dancer_vectors) + noise",
      "reference": "von Frisch 1967"
    },
    {
      "phenomenon": "ant_quorum",
      "algorithm": "quorum_commit",
      "params": [
        "threshold",
        "recruit_rate"
      ],
      "math": "commit when n_recruited >= threshold",
      "reference": "Pratt 2002, PNAS 99:10421"
    },
    {
      "phenomenon": "ant_colony",
      "algorithm": "aco_pheromone",
      "params": [
        "evaporation",
        "deposit",
        "alpha",
        "beta"
      ],
      "math": "tau_{ij} <- (1-rho)*tau_{ij} + sum d_tau",
      "reference": "Dorigo 1992"
    },
    {
      "phenomenon": "termite_mound",
      "algorithm": "stigmergy_build",
      "params": [
        "deposit_rate",
        "evaporation_rate"
      ],
      "math": "field[x] += deposit; field[x] *= (1 - evap)",
      "reference": "Theraulaz 1995"
    },
    {
      "phenomenon": "slime_mold",
      "algorithm": "tube_reinforcement",
      "params": [
        "conductivity_rate",
        "decay"
      ],
      "math": "D_{ij} += f(flux_{ij}); D_{ij} *= (1-decay)",
      "reference": "Tero 2007"
    },
    {
      "phenomenon": "boids",
      "algorithm": "boids_rule",
      "params": [
        "separation",
        "alignment",
        "cohesion",
        "r"
      ],
      "math": "v_i += w_s*sep + w_a*align + w_c*coh",
      "reference": "Reynolds 1987"
    },
    {
      "phenomenon": "starling_murmuration",
      "algorithm": "topological_flock",
      "params": [
        "k_neighbours",
        "w_sep",
        "w_ali",
        "w_coh"
      ],
      "math": "v_i <- mean(v of k nearest); k=7",
      "reference": "Ballerini 2008"
    },
    {
      "phenomenon": "murmuration_critical",
      "algorithm": "critical_flock",
      "params": [
        "density",
        "noise"
      ],
      "math": "order parameter peaks at critical density",
      "reference": "Cavagna 2010"
    },
    {
      "phenomenon": "fish_school",
      "algorithm": "school_edge_follow",
      "params": [
        "edge_weight",
        "predator_repulsion"
      ],
      "math": "v_i <- edge_direction + repulsion",
      "reference": "Hemelrijk 2015"
    },
    {
      "phenomenon": "locust_swarm",
      "algorithm": "cannibal_band",
      "params": [
        "alignment",
        "repulsion"
      ],
      "math": "v_i <- align + repel",
      "reference": "Buhl 2006, Science 312:1402"
    },
    {
      "phenomenon": "kuramoto",
      "algorithm": "kuramoto_step",
      "params": [
        "K",
        "omega",
        "dt"
      ],
      "math": "dtheta_i/dt = omega_i + (K/N) sum sin(theta_j - theta_i)",
      "reference": "Kuramoto 1975"
    },
    {
      "phenomenon": "firefly_sync",
      "algorithm": "pulse_coupled",
      "params": [
        "epsilon",
        "period"
      ],
      "math": "on pulse: theta_j <- theta_j + epsilon",
      "reference": "Mirollo & Strogatz 1990"
    },
    {
      "phenomenon": "cricket_chorus",
      "algorithm": "leader_coupling",
      "params": [
        "coupling",
        "noise"
      ],
      "math": "strong coupling -> leader emerges",
      "reference": "Greenfield 1994"
    },
    {
      "phenomenon": "fitzhugh_nagumo",
      "algorithm": "fn_integrate",
      "params": [
        "a",
        "b",
        "I",
        "dt"
      ],
      "math": "dv/dt = v - v^3/3 - w + I; dw/dt = (v + a - b*w)/tau",
      "reference": "FitzHugh 1961"
    },
    {
      "phenomenon": "hodgkin_huxley",
      "algorithm": "hh_integrate",
      "params": [
        "g_Na",
        "g_K",
        "g_L",
        "C_m",
        "dt"
      ],
      "math": "C dV/dt = I - sum(I_ion)",
      "reference": "Hodgkin & Huxley 1952"
    },
    {
      "phenomenon": "circadian_clock",
      "algorithm": "goodwin_oscillator",
      "params": [
        "k1",
        "k2",
        "k3",
        "n",
        "dt"
      ],
      "math": "delayed negative feedback with Hill coefficient",
      "reference": "Goodwin 1965"
    },
    {
      "phenomenon": "turing_pattern",
      "algorithm": "reaction_diffusion",
      "params": [
        "Du",
        "Dv",
        "f",
        "k",
        "dt"
      ],
      "math": "du/dt = Du lap(u) + u - u^3 - v",
      "reference": "Turing 1952"
    },
    {
      "phenomenon": "gray_scott",
      "algorithm": "gray_scott_step",
      "params": [
        "Du",
        "Dv",
        "F",
        "k",
        "dt"
      ],
      "math": "du/dt = Du lap(u) - u v^2 + F(1-u)",
      "reference": "Gray & Scott 1984"
    },
    {
      "phenomenon": "belousov_zhabotinsky",
      "algorithm": "bz_oregonator",
      "params": [
        "eps",
        "q",
        "f",
        "dt"
      ],
      "math": "Oregonator equations",
      "reference": "Field & Noyes 1974"
    },
    {
      "phenomenon": "dla",
      "algorithm": "diffusion_limited_aggregation",
      "params": [
        "N_particles",
        "sticking_prob"
      ],
      "math": "random walk until attach",
      "reference": "Witten & Sander 1981"
    },
    {
      "phenomenon": "eden_growth",
      "algorithm": "eden_model",
      "params": [
        "p",
        "N"
      ],
      "math": "attach randomly to boundary",
      "reference": "Eden 1961"
    },
    {
      "phenomenon": "lichen_edge",
      "algorithm": "boundary_expansion",
      "params": [
        "rate"
      ],
      "math": "slow boundary expansion",
      "reference": "Watson 2014"
    },
    {
      "phenomenon": "tree_branching",
      "algorithm": "l_system",
      "params": [
        "axiom",
        "rules",
        "angle",
        "iterations"
      ],
      "math": "L-system rewriting",
      "reference": "Prusinkiewicz 1990"
    },
    {
      "phenomenon": "elephant_walk",
      "algorithm": "memory_walk",
      "params": [
        "step",
        "memory",
        "weight"
      ],
      "math": "next = weighted mix of past positions",
      "reference": "Moorcroft 2006"
    },
    {
      "phenomenon": "self_avoiding_walk",
      "algorithm": "saw_walk",
      "params": [
        "N",
        "lattice"
      ],
      "math": "grow path, reject revisits",
      "reference": "Flory 1949"
    },
    {
      "phenomenon": "persistent_walk",
      "algorithm": "correlated_walk",
      "params": [
        "step",
        "kappa",
        "dt"
      ],
      "math": "theta_{n+1} = theta_n + N(0, kappa^2)",
      "reference": "Kareiva 1983"
    },
    {
      "phenomenon": "levy_walk_2d",
      "algorithm": "levy_walk_2d",
      "params": [
        "alpha",
        "scale"
      ],
      "math": "2D heavy-tail search",
      "reference": "Viswanathan 1999"
    },
    {
      "phenomenon": "quorum_sensing",
      "algorithm": "density_gate",
      "params": [
        "threshold",
        "signal"
      ],
      "math": "act if signal >= threshold",
      "reference": "Miller & Bassler 2001"
    },
    {
      "phenomenon": "all_or_none",
      "algorithm": "sigmoid_response",
      "params": [
        "gain",
        "threshold"
      ],
      "math": "y = 1 / (1 + exp(-gain(x - threshold)))",
      "reference": "Hill 1910"
    },
    {
      "phenomenon": "neuron_threshold",
      "algorithm": "lif_neuron",
      "params": [
        "tau_m",
        "V_th",
        "V_reset",
        "dt"
      ],
      "math": "tau_m dV/dt = -(V - V_rest) + R I",
      "reference": "Lapicque 1907"
    },
    {
      "phenomenon": "gene_switch",
      "algorithm": "toggle_switch",
      "params": [
        "alpha1",
        "alpha2",
        "beta",
        "n"
      ],
      "math": "bistable two mutually repressing genes",
      "reference": "Gardner 2000"
    },
    {
      "phenomenon": "phase_transition",
      "algorithm": "ising_order",
      "params": [
        "J",
        "T",
        "N"
      ],
      "math": "m = tanh(J m / T)",
      "reference": "Onsager 1944"
    },
    {
      "phenomenon": "habituation",
      "algorithm": "habituation_step",
      "params": [
        "rate",
        "floor"
      ],
      "math": "response <- max(floor, response * (1 - rate))",
      "reference": "Thompson & Spencer 1966"
    },
    {
      "phenomenon": "sensitization",
      "algorithm": "sensitization_step",
      "params": [
        "rate",
        "ceiling"
      ],
      "math": "response <- min(ceiling, response * (1 + rate))",
      "reference": "Groves & Thompson 1970"
    },
    {
      "phenomenon": "hebbian",
      "algorithm": "hebbian_update",
      "params": [
        "eta"
      ],
      "math": "dw_{ij} = eta * x_i * x_j",
      "reference": "Hebb 1949"
    },
    {
      "phenomenon": "stdp",
      "algorithm": "stdp_update",
      "params": [
        "A_plus",
        "A_minus",
        "tau_plus",
        "tau_minus"
      ],
      "math": "dw = A_plus exp(-dt/tau_plus)",
      "reference": "Bi & Poo 1998"
    },
    {
      "phenomenon": "homeostasis",
      "algorithm": "negative_feedback",
      "params": [
        "setpoint",
        "gain",
        "dt"
      ],
      "math": "dx/dt = -gain * (x - setpoint)",
      "reference": "Cannon 1932"
    },
    {
      "phenomenon": "allostasis",
      "algorithm": "predictive_control",
      "params": [
        "gain",
        "horizon",
        "dt"
      ],
      "math": "x_target = predict(future demand)",
      "reference": "Sterling & Eyer 1988"
    },
    {
      "phenomenon": "immune_affinity",
      "algorithm": "clonal_selection",
      "params": [
        "mutation_rate",
        "selection_pressure"
      ],
      "math": "clone + mutate; select by affinity",
      "reference": "Burnet 1959"
    },
    {
      "phenomenon": "bacterial_chemotaxis",
      "algorithm": "run_and_tumble",
      "params": [
        "run_length",
        "tumble_prob"
      ],
      "math": "run if gradient positive",
      "reference": "Berg & Brown 1972"
    },
    {
      "phenomenon": "lotka_volterra",
      "algorithm": "lv_step",
      "params": [
        "alpha",
        "beta",
        "delta",
        "gamma",
        "dt"
      ],
      "math": "dx/dt = alpha x - beta x y; dy/dt = delta x y - gamma y",
      "reference": "Lotka 1925"
    },
    {
      "phenomenon": "logistic",
      "algorithm": "logistic_growth",
      "params": [
        "r",
        "K",
        "dt"
      ],
      "math": "dx/dt = r x (1 - x/K)",
      "reference": "Verhulst 1838"
    },
    {
      "phenomenon": "gompertz",
      "algorithm": "gompertz_growth",
      "params": [
        "a",
        "b",
        "dt"
      ],
      "math": "dx/dt = a x exp(-b t)",
      "reference": "Gompertz 1825"
    },
    {
      "phenomenon": "allee",
      "algorithm": "allee_growth",
      "params": [
        "r",
        "K",
        "A",
        "dt"
      ],
      "math": "dx/dt = r x (x/A - 1)(1 - x/K)",
      "reference": "Allee 1931"
    },
    {
      "phenomenon": "sir",
      "algorithm": "sir_step",
      "params": [
        "beta",
        "gamma",
        "dt"
      ],
      "math": "dS/dt = -beta S I / N; dI/dt = beta S I / N - gamma I",
      "reference": "Kermack & McKendrick 1927"
    },
    {
      "phenomenon": "sirs",
      "algorithm": "sirs_step",
      "params": [
        "beta",
        "gamma",
        "omega",
        "dt"
      ],
      "math": "SIRS with waning immunity",
      "reference": "Kermack & McKendrick 1932"
    },
    {
      "phenomenon": "host_parasite",
      "algorithm": "red_queen",
      "params": [
        "mutation",
        "selection"
      ],
      "math": "coevolving genotype frequencies",
      "reference": "Van Valen 1973"
    },
    {
      "phenomenon": "predator_prey_spatial",
      "algorithm": "spatial_lv",
      "params": [
        "alpha",
        "beta",
        "delta",
        "gamma",
        "Dx",
        "Dy",
        "dt"
      ],
      "math": "Turing-Holling on grid",
      "reference": "Holling 1959"
    },
    {
      "phenomenon": "fick",
      "algorithm": "fick_flux",
      "params": [
        "D",
        "dt"
      ],
      "math": "J = -D grad(c)",
      "reference": "Fick 1855"
    },
    {
      "phenomenon": "darcy",
      "algorithm": "darcy_flow",
      "params": [
        "k",
        "mu",
        "dt"
      ],
      "math": "v = -(k/mu) grad(P)",
      "reference": "Darcy 1856"
    },
    {
      "phenomenon": "poiseuille",
      "algorithm": "poiseuille_flow",
      "params": [
        "mu",
        "R",
        "L"
      ],
      "math": "Q = pi R^4 dP / (8 mu L)",
      "reference": "Poiseuille 1840"
    },
    {
      "phenomenon": "kirchhoff",
      "algorithm": "conservation_law",
      "params": [
        "topology"
      ],
      "math": "sum of currents at node = 0",
      "reference": "Kirchhoff 1845"
    },
    {
      "phenomenon": "fourier",
      "algorithm": "heat_conduction",
      "params": [
        "k",
        "rho",
        "c",
        "dt"
      ],
      "math": "dT/dt = (k / (rho c)) lap(T)",
      "reference": "Fourier 1822"
    },
    {
      "phenomenon": "nernst",
      "algorithm": "nernst_planck",
      "params": [
        "D",
        "z",
        "F",
        "R",
        "T",
        "dt"
      ],
      "math": "J = -D grad(c) - (D z F c / R T) grad(phi)",
      "reference": "Nernst 1888"
    },
    {
      "phenomenon": "chemostat",
      "algorithm": "chemostat_step",
      "params": [
        "D",
        "c_in",
        "mu_max",
        "K_s",
        "dt"
      ],
      "math": "dc/dt = D(c_in - c) - mu(c) x",
      "reference": "Monod 1950"
    },
    {
      "phenomenon": "osmosis",
      "algorithm": "osmotic_flow",
      "params": [
        "A",
        "P_osmotic",
        "dt"
      ],
      "math": "J_v = A L_p (dP - dPi)",
      "reference": "van 't Hoff 1887"
    },
    {
      "phenomenon": "diffusion_limited",
      "algorithm": "boundary_reaction",
      "params": [
        "D",
        "k",
        "dt"
      ],
      "math": "reaction at boundary",
      "reference": "Rice 1985"
    }
  ]
}```
