Development preparation / observations

REACT v4: forcedP16 versus forcedP16+react. No scientific verdict or acceptance.

Mechanism first: D2, 10 paired seeds / 20 actual fights.
Counts are own successful dodge intent ticks, not independent evade events. Shell ratios include zero-hit landed enemy shells; unresolved shells are censored. Damage units are HP. Null means no denominator.
All summaries show their n; paired differences are react minus base. Pooled shell ratios are shell-weighted; paired ratios average per-fight differences over pairs with both denominators.
Won fights and all non-wins (losses/timeouts/draws) have separate loss denominators.

Mechanism:
```json
{
  "arms": {
    "forcedP16": {
      "n": 0,
      "wins": 0,
      "own_losses_on_wins": {
        "n": 0,
        "mean": null
      },
      "own_losses_on_nonwins": {
        "n": 0,
        "mean": null
      },
      "dodges_per_fight": {
        "n": 0,
        "mean": null
      },
      "enemy_shells_landed": 0,
      "hit_units": 0,
      "shell_damage": 0,
      "own_units_hit_per_landed_enemy_shell": null,
      "damage_taken_per_landed_enemy_shell": null,
      "unassigned_enemy_artillery_damage": 0,
      "unresolved_enemy_shells": 0
    },
    "forcedP16+react": {
      "n": 0,
      "wins": 0,
      "own_losses_on_wins": {
        "n": 0,
        "mean": null
      },
      "own_losses_on_nonwins": {
        "n": 0,
        "mean": null
      },
      "dodges_per_fight": {
        "n": 0,
        "mean": null
      },
      "enemy_shells_landed": 0,
      "hit_units": 0,
      "shell_damage": 0,
      "own_units_hit_per_landed_enemy_shell": null,
      "damage_taken_per_landed_enemy_shell": null,
      "unassigned_enemy_artillery_damage": 0,
      "unresolved_enemy_shells": 0
    }
  },
  "paired": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "paired_losses_both_won": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "paired_losses_both_nonwin": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "stage": "mechanism",
  "look": 10,
  "complete": false,
  "declaration_sha256": "65850e8427cdc540d984ca90c278b26254a1ecbc0299fcab43796ce4e700dc6e"
}
```

C3 sequential look 50 paired fights (total across 20 opponents):
```json
{
  "arms": {
    "forcedP16": {
      "n": 0,
      "wins": 0,
      "own_losses_on_wins": {
        "n": 0,
        "mean": null
      },
      "own_losses_on_nonwins": {
        "n": 0,
        "mean": null
      },
      "dodges_per_fight": {
        "n": 0,
        "mean": null
      },
      "enemy_shells_landed": 0,
      "hit_units": 0,
      "shell_damage": 0,
      "own_units_hit_per_landed_enemy_shell": null,
      "damage_taken_per_landed_enemy_shell": null,
      "unassigned_enemy_artillery_damage": 0,
      "unresolved_enemy_shells": 0
    },
    "forcedP16+react": {
      "n": 0,
      "wins": 0,
      "own_losses_on_wins": {
        "n": 0,
        "mean": null
      },
      "own_losses_on_nonwins": {
        "n": 0,
        "mean": null
      },
      "dodges_per_fight": {
        "n": 0,
        "mean": null
      },
      "enemy_shells_landed": 0,
      "hit_units": 0,
      "shell_damage": 0,
      "own_units_hit_per_landed_enemy_shell": null,
      "damage_taken_per_landed_enemy_shell": null,
      "unassigned_enemy_artillery_damage": 0,
      "unresolved_enemy_shells": 0
    }
  },
  "paired": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "paired_losses_both_won": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "paired_losses_both_nonwin": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "stage": "outcome",
  "look": 50,
  "complete": false,
  "declaration_sha256": "65850e8427cdc540d984ca90c278b26254a1ecbc0299fcab43796ce4e700dc6e",
  "per_tactic": {}
}
```

C3 sequential look 100 paired fights (total across 20 opponents):
```json
{
  "arms": {
    "forcedP16": {
      "n": 0,
      "wins": 0,
      "own_losses_on_wins": {
        "n": 0,
        "mean": null
      },
      "own_losses_on_nonwins": {
        "n": 0,
        "mean": null
      },
      "dodges_per_fight": {
        "n": 0,
        "mean": null
      },
      "enemy_shells_landed": 0,
      "hit_units": 0,
      "shell_damage": 0,
      "own_units_hit_per_landed_enemy_shell": null,
      "damage_taken_per_landed_enemy_shell": null,
      "unassigned_enemy_artillery_damage": 0,
      "unresolved_enemy_shells": 0
    },
    "forcedP16+react": {
      "n": 0,
      "wins": 0,
      "own_losses_on_wins": {
        "n": 0,
        "mean": null
      },
      "own_losses_on_nonwins": {
        "n": 0,
        "mean": null
      },
      "dodges_per_fight": {
        "n": 0,
        "mean": null
      },
      "enemy_shells_landed": 0,
      "hit_units": 0,
      "shell_damage": 0,
      "own_units_hit_per_landed_enemy_shell": null,
      "damage_taken_per_landed_enemy_shell": null,
      "unassigned_enemy_artillery_damage": 0,
      "unresolved_enemy_shells": 0
    }
  },
  "paired": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "paired_losses_both_won": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "paired_losses_both_nonwin": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "stage": "outcome",
  "look": 100,
  "complete": false,
  "declaration_sha256": "65850e8427cdc540d984ca90c278b26254a1ecbc0299fcab43796ce4e700dc6e",
  "per_tactic": {}
}
```

C3 sequential look 200 paired fights (total across 20 opponents):
```json
{
  "arms": {
    "forcedP16": {
      "n": 0,
      "wins": 0,
      "own_losses_on_wins": {
        "n": 0,
        "mean": null
      },
      "own_losses_on_nonwins": {
        "n": 0,
        "mean": null
      },
      "dodges_per_fight": {
        "n": 0,
        "mean": null
      },
      "enemy_shells_landed": 0,
      "hit_units": 0,
      "shell_damage": 0,
      "own_units_hit_per_landed_enemy_shell": null,
      "damage_taken_per_landed_enemy_shell": null,
      "unassigned_enemy_artillery_damage": 0,
      "unresolved_enemy_shells": 0
    },
    "forcedP16+react": {
      "n": 0,
      "wins": 0,
      "own_losses_on_wins": {
        "n": 0,
        "mean": null
      },
      "own_losses_on_nonwins": {
        "n": 0,
        "mean": null
      },
      "dodges_per_fight": {
        "n": 0,
        "mean": null
      },
      "enemy_shells_landed": 0,
      "hit_units": 0,
      "shell_damage": 0,
      "own_units_hit_per_landed_enemy_shell": null,
      "damage_taken_per_landed_enemy_shell": null,
      "unassigned_enemy_artillery_damage": 0,
      "unresolved_enemy_shells": 0
    }
  },
  "paired": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "paired_losses_both_won": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "paired_losses_both_nonwin": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "stage": "outcome",
  "look": 200,
  "complete": false,
  "declaration_sha256": "65850e8427cdc540d984ca90c278b26254a1ecbc0299fcab43796ce4e700dc6e",
  "per_tactic": {}
}
```

S10X: streak is primary. Ten paired series, at most ten fights each; first non-win stops that arm.
```json
{
  "complete": false,
  "primary": "streak distribution and paired streak difference",
  "series": [],
  "arms": {
    "forcedP16": {
      "n_series": 0,
      "streak_distribution": {},
      "mean_streak": {
        "n": 0,
        "mean": null
      },
      "reach": [
        {
          "fight": 1,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 2,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 3,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 4,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 5,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 6,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 7,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 8,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 9,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 10,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        }
      ],
      "fights": {
        "n": 0,
        "wins": 0,
        "own_losses_on_wins": {
          "n": 0,
          "mean": null
        },
        "own_losses_on_nonwins": {
          "n": 0,
          "mean": null
        },
        "dodges_per_fight": {
          "n": 0,
          "mean": null
        },
        "enemy_shells_landed": 0,
        "hit_units": 0,
        "shell_damage": 0,
        "own_units_hit_per_landed_enemy_shell": null,
        "damage_taken_per_landed_enemy_shell": null,
        "unassigned_enemy_artillery_damage": 0,
        "unresolved_enemy_shells": 0
      },
      "per_tactic": {}
    },
    "forcedP16+react": {
      "n_series": 0,
      "streak_distribution": {},
      "mean_streak": {
        "n": 0,
        "mean": null
      },
      "reach": [
        {
          "fight": 1,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 2,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 3,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 4,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 5,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 6,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 7,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 8,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 9,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        },
        {
          "fight": 10,
          "n": 0,
          "denominator": 0,
          "units_before": {
            "n": 0,
            "mean": null
          },
          "role_units_before": {
            "melee": {
              "n": 0,
              "mean": null
            },
            "ranged": {
              "n": 0,
              "mean": null
            },
            "artillery": {
              "n": 0,
              "mean": null
            }
          }
        }
      ],
      "fights": {
        "n": 0,
        "wins": 0,
        "own_losses_on_wins": {
          "n": 0,
          "mean": null
        },
        "own_losses_on_nonwins": {
          "n": 0,
          "mean": null
        },
        "dodges_per_fight": {
          "n": 0,
          "mean": null
        },
        "enemy_shells_landed": 0,
        "hit_units": 0,
        "shell_damage": 0,
        "own_units_hit_per_landed_enemy_shell": null,
        "damage_taken_per_landed_enemy_shell": null,
        "unassigned_enemy_artillery_damage": 0,
        "unresolved_enemy_shells": 0
      },
      "per_tactic": {}
    }
  },
  "paired_streak_difference": {
    "direction": "react minus base",
    "n": 0,
    "mean": null
  },
  "paired_reached_fights": {
    "n": 0,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 0,
        "mean": null
      },
      "own_lost": {
        "n": 0,
        "mean": null
      },
      "own_dodges": {
        "n": 0,
        "mean": null
      },
      "own_units_hit_per_enemy_shell": {
        "n": 0,
        "mean": null
      },
      "damage_taken_per_enemy_shell": {
        "n": 0,
        "mean": null
      }
    }
  },
  "reached_limit": "Fight differences use only positions reached by both arms, with differing carried cohorts; conditioning on survival is descriptive."
}
```

Elite reference: ../s4_shape_lab_v3/SHAPE_LAB_REPORT.md and S10X_SUMMARY.json (historical, unpaired).
C3 retains v3 abilities settings; S10X abilities off, survivors healed, dead cohort IDs absent. Map seed and orientation are identical for both arms at each scheduled position; survivor populations diverge by design.
C3 50/100/200 is not 200 per tactic. Individual tactic samples are descriptive (2–3, 5, 10 pairs); no fine per-tactic claims.
At each look Claude records continue/stop before more C3 fights. No automatic significance rule or tuning; stop or park at 200.
Calibration reuses allocated fights. Cap bounds native execution per invocation; bookkeeping/rendering may finish afterwards. No elapsed timing is claimed before calibration.
