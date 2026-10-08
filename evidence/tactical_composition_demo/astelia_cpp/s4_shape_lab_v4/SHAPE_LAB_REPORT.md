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
      "n": 10,
      "wins": 10,
      "own_losses_on_wins": {
        "n": 10,
        "mean": 20.1
      },
      "own_losses_on_nonwins": {
        "n": 0,
        "mean": null
      },
      "dodges_per_fight": {
        "n": 10,
        "mean": 0.0
      },
      "enemy_shells_landed": 404,
      "hit_units": 1744,
      "shell_damage": 23573.0,
      "own_units_hit_per_landed_enemy_shell": 4.316831683168317,
      "damage_taken_per_landed_enemy_shell": 58.3490099009901,
      "unassigned_enemy_artillery_damage": 0.0,
      "unresolved_enemy_shells": 6
    },
    "forcedP16+react": {
      "n": 10,
      "wins": 10,
      "own_losses_on_wins": {
        "n": 10,
        "mean": 11.4
      },
      "own_losses_on_nonwins": {
        "n": 0,
        "mean": null
      },
      "dodges_per_fight": {
        "n": 10,
        "mean": 1779.8
      },
      "enemy_shells_landed": 564,
      "hit_units": 1002,
      "shell_damage": 13568.0,
      "own_units_hit_per_landed_enemy_shell": 1.7765957446808511,
      "damage_taken_per_landed_enemy_shell": 24.05673758865248,
      "unassigned_enemy_artillery_damage": 0.0,
      "unresolved_enemy_shells": 6
    }
  },
  "paired": {
    "n": 10,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 10,
        "mean": 0.0
      },
      "own_lost": {
        "n": 10,
        "mean": -8.7
      },
      "own_dodges": {
        "n": 10,
        "mean": 1779.8
      },
      "own_units_hit_per_enemy_shell": {
        "n": 10,
        "mean": -2.55462659358073
      },
      "damage_taken_per_enemy_shell": {
        "n": 10,
        "mean": -34.48521127101955
      }
    }
  },
  "paired_losses_both_won": {
    "n": 10,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 10,
        "mean": 0.0
      },
      "own_lost": {
        "n": 10,
        "mean": -8.7
      },
      "own_dodges": {
        "n": 10,
        "mean": 1779.8
      },
      "own_units_hit_per_enemy_shell": {
        "n": 10,
        "mean": -2.55462659358073
      },
      "damage_taken_per_enemy_shell": {
        "n": 10,
        "mean": -34.48521127101955
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
  "complete": true,
  "declaration_sha256": "65850e8427cdc540d984ca90c278b26254a1ecbc0299fcab43796ce4e700dc6e"
}
```

C3 sequential look 50 paired fights (total across 20 opponents):
```json
{
  "arms": {
    "forcedP16": {
      "n": 50,
      "wins": 26,
      "own_losses_on_wins": {
        "n": 26,
        "mean": 41.92307692307692
      },
      "own_losses_on_nonwins": {
        "n": 24,
        "mean": 50.0
      },
      "dodges_per_fight": {
        "n": 50,
        "mean": 0.0
      },
      "enemy_shells_landed": 4570,
      "hit_units": 17535,
      "shell_damage": 239923.0,
      "own_units_hit_per_landed_enemy_shell": 3.836980306345733,
      "damage_taken_per_landed_enemy_shell": 52.49956236323851,
      "unassigned_enemy_artillery_damage": 0.0,
      "unresolved_enemy_shells": 19
    },
    "forcedP16+react": {
      "n": 50,
      "wins": 46,
      "own_losses_on_wins": {
        "n": 46,
        "mean": 35.28260869565217
      },
      "own_losses_on_nonwins": {
        "n": 4,
        "mean": 50.0
      },
      "dodges_per_fight": {
        "n": 50,
        "mean": 10667.18
      },
      "enemy_shells_landed": 8050,
      "hit_units": 13794,
      "shell_damage": 190096.0,
      "own_units_hit_per_landed_enemy_shell": 1.7135403726708074,
      "damage_taken_per_landed_enemy_shell": 23.614409937888198,
      "unassigned_enemy_artillery_damage": 0.0,
      "unresolved_enemy_shells": 17
    }
  },
  "paired": {
    "n": 50,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 50,
        "mean": 0.4
      },
      "own_lost": {
        "n": 50,
        "mean": -9.34
      },
      "own_dodges": {
        "n": 50,
        "mean": 10667.18
      },
      "own_units_hit_per_enemy_shell": {
        "n": 50,
        "mean": -2.2583069813350165
      },
      "damage_taken_per_enemy_shell": {
        "n": 50,
        "mean": -30.659974576684775
      }
    }
  },
  "paired_losses_both_won": {
    "n": 26,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 26,
        "mean": 0.0
      },
      "own_lost": {
        "n": 26,
        "mean": -8.576923076923077
      },
      "own_dodges": {
        "n": 26,
        "mean": 10776.076923076924
      },
      "own_units_hit_per_enemy_shell": {
        "n": 26,
        "mean": -2.709311769939266
      },
      "damage_taken_per_enemy_shell": {
        "n": 26,
        "mean": -36.57655141163986
      }
    }
  },
  "paired_losses_both_nonwin": {
    "n": 4,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 4,
        "mean": 0.0
      },
      "own_lost": {
        "n": 4,
        "mean": 0.0
      },
      "own_dodges": {
        "n": 4,
        "mean": 10369.75
      },
      "own_units_hit_per_enemy_shell": {
        "n": 4,
        "mean": -1.7863123179630276
      },
      "damage_taken_per_enemy_shell": {
        "n": 4,
        "mean": -24.34759799461091
      }
    }
  },
  "stage": "outcome",
  "look": 50,
  "complete": true,
  "declaration_sha256": "65850e8427cdc540d984ca90c278b26254a1ecbc0299fcab43796ce4e700dc6e",
  "per_tactic": {
    "alone": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 210,
          "hit_units": 638,
          "shell_damage": 8750.0,
          "own_units_hit_per_landed_enemy_shell": 3.038095238095238,
          "damage_taken_per_landed_enemy_shell": 41.666666666666664,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 22.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 6997.0
          },
          "enemy_shells_landed": 224,
          "hit_units": 432,
          "shell_damage": 5982.0,
          "own_units_hit_per_landed_enemy_shell": 1.9285714285714286,
          "damage_taken_per_landed_enemy_shell": 26.705357142857142,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 1.0
          },
          "own_lost": {
            "n": 2,
            "mean": -28.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 6997.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.0975419249533165
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -14.78782750219666
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
      }
    },
    "box": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 39.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 210,
          "hit_units": 1082,
          "shell_damage": 14659.0,
          "own_units_hit_per_landed_enemy_shell": 5.152380952380953,
          "damage_taken_per_landed_enemy_shell": 69.8047619047619,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 33.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 8659.0
          },
          "enemy_shells_landed": 421,
          "hit_units": 807,
          "shell_damage": 11105.0,
          "own_units_hit_per_landed_enemy_shell": 1.9168646080760094,
          "damage_taken_per_landed_enemy_shell": 26.377672209026127,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -6.333333333333333
          },
          "own_dodges": {
            "n": 3,
            "mean": 8659.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -3.2510847715722626
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -43.611967205166586
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -6.333333333333333
          },
          "own_dodges": {
            "n": 3,
            "mean": 8659.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -3.2510847715722626
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -43.611967205166586
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
      }
    },
    "column": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 40.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 224,
          "hit_units": 1025,
          "shell_damage": 13885.0,
          "own_units_hit_per_landed_enemy_shell": 4.575892857142857,
          "damage_taken_per_landed_enemy_shell": 61.986607142857146,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 28.333333333333332
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 9015.666666666666
          },
          "enemy_shells_landed": 373,
          "hit_units": 805,
          "shell_damage": 11127.0,
          "own_units_hit_per_landed_enemy_shell": 2.158176943699732,
          "damage_taken_per_landed_enemy_shell": 29.831099195710454,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -12.333333333333334
          },
          "own_dodges": {
            "n": 3,
            "mean": 9015.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.470853584057176
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -32.82798573541285
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -12.333333333333334
          },
          "own_dodges": {
            "n": 3,
            "mean": 9015.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.470853584057176
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -32.82798573541285
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
      }
    },
    "crescent": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 44.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 291,
          "hit_units": 1121,
          "shell_damage": 15345.0,
          "own_units_hit_per_landed_enemy_shell": 3.852233676975945,
          "damage_taken_per_landed_enemy_shell": 52.7319587628866,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 38.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 9679.666666666666
          },
          "enemy_shells_landed": 517,
          "hit_units": 902,
          "shell_damage": 12448.0,
          "own_units_hit_per_landed_enemy_shell": 1.7446808510638299,
          "damage_taken_per_landed_enemy_shell": 24.077369439071568,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.3333333333333333
          },
          "own_lost": {
            "n": 3,
            "mean": -7.666666666666667
          },
          "own_dodges": {
            "n": 3,
            "mean": 9679.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.100081076504022
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.551382820354068
          }
        }
      },
      "paired_losses_both_won": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": -6.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 9959.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.015152289602659
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -27.642529395679517
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
      }
    },
    "line": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 44.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 312,
          "hit_units": 1141,
          "shell_damage": 15637.0,
          "own_units_hit_per_landed_enemy_shell": 3.657051282051282,
          "damage_taken_per_landed_enemy_shell": 50.118589743589745,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 37.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11541.333333333334
          },
          "enemy_shells_landed": 559,
          "hit_units": 891,
          "shell_damage": 12195.0,
          "own_units_hit_per_landed_enemy_shell": 1.5939177101967799,
          "damage_taken_per_landed_enemy_shell": 21.815742397137747,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -7.333333333333333
          },
          "own_dodges": {
            "n": 3,
            "mean": 11541.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.0670787005801396
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.35761861407246
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -7.333333333333333
          },
          "own_dodges": {
            "n": 3,
            "mean": 11541.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.0670787005801396
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.35761861407246
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
      }
    },
    "line anvil": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 201,
          "hit_units": 773,
          "shell_damage": 10647.0,
          "own_units_hit_per_landed_enemy_shell": 3.845771144278607,
          "damage_taken_per_landed_enemy_shell": 52.97014925373134,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 42.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 11696.0
          },
          "enemy_shells_landed": 411,
          "hit_units": 650,
          "shell_damage": 8976.0,
          "own_units_hit_per_landed_enemy_shell": 1.5815085158150852,
          "damage_taken_per_landed_enemy_shell": 21.83941605839416,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 1.0
          },
          "own_lost": {
            "n": 2,
            "mean": -8.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 11696.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.2627753374076907
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -31.101788101604278
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
      }
    },
    "loose": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 3,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 332,
          "hit_units": 1052,
          "shell_damage": 14442.0,
          "own_units_hit_per_landed_enemy_shell": 3.1686746987951806,
          "damage_taken_per_landed_enemy_shell": 43.5,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 41.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 12063.333333333334
          },
          "enemy_shells_landed": 528,
          "hit_units": 853,
          "shell_damage": 11809.0,
          "own_units_hit_per_landed_enemy_shell": 1.615530303030303,
          "damage_taken_per_landed_enemy_shell": 22.365530303030305,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 1.0
          },
          "own_lost": {
            "n": 3,
            "mean": -8.333333333333334
          },
          "own_dodges": {
            "n": 3,
            "mean": 12063.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -1.54425769445871
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -20.99992801882351
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
      }
    },
    "loose berserk": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 196,
          "hit_units": 585,
          "shell_damage": 8084.0,
          "own_units_hit_per_landed_enemy_shell": 2.9846938775510203,
          "damage_taken_per_landed_enemy_shell": 41.244897959183675,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 40.5
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 7554.0
          },
          "enemy_shells_landed": 310,
          "hit_units": 489,
          "shell_damage": 6727.0,
          "own_units_hit_per_landed_enemy_shell": 1.5774193548387097,
          "damage_taken_per_landed_enemy_shell": 21.7,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 1.0
          },
          "own_lost": {
            "n": 2,
            "mean": -9.5
          },
          "own_dodges": {
            "n": 2,
            "mean": 7554.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.4118182267599186
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -19.600599891761377
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
      }
    },
    "loose free": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 152,
          "hit_units": 393,
          "shell_damage": 5408.0,
          "own_units_hit_per_landed_enemy_shell": 2.585526315789474,
          "damage_taken_per_landed_enemy_shell": 35.578947368421055,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 40.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 7611.0
          },
          "enemy_shells_landed": 333,
          "hit_units": 427,
          "shell_damage": 5843.0,
          "own_units_hit_per_landed_enemy_shell": 1.2822822822822824,
          "damage_taken_per_landed_enemy_shell": 17.546546546546548,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.5
          },
          "own_lost": {
            "n": 2,
            "mean": -5.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 7611.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.290461921690972
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -17.838752085902925
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
        "n": 1,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 1,
            "mean": 0.0
          },
          "own_lost": {
            "n": 1,
            "mean": 0.0
          },
          "own_dodges": {
            "n": 1,
            "mean": 7196.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 1,
            "mean": -1.028975791433892
          },
          "damage_taken_per_enemy_shell": {
            "n": 1,
            "mean": -13.807374301675978
          }
        }
      }
    },
    "loose skirmish": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 207,
          "hit_units": 740,
          "shell_damage": 10170.0,
          "own_units_hit_per_landed_enemy_shell": 3.57487922705314,
          "damage_taken_per_landed_enemy_shell": 49.130434782608695,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 36.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 12640.5
          },
          "enemy_shells_landed": 314,
          "hit_units": 515,
          "shell_damage": 7058.0,
          "own_units_hit_per_landed_enemy_shell": 1.6401273885350318,
          "damage_taken_per_landed_enemy_shell": 22.477707006369428,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 1.0
          },
          "own_lost": {
            "n": 2,
            "mean": -14.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 12640.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.9360943312847019
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -26.66947672092849
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
      }
    },
    "regular": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 44.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 326,
          "hit_units": 1150,
          "shell_damage": 15785.0,
          "own_units_hit_per_landed_enemy_shell": 3.5276073619631902,
          "damage_taken_per_landed_enemy_shell": 48.420245398773005,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 36.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11477.333333333334
          },
          "enemy_shells_landed": 503,
          "hit_units": 878,
          "shell_damage": 12162.0,
          "own_units_hit_per_landed_enemy_shell": 1.7455268389662029,
          "damage_taken_per_landed_enemy_shell": 24.178926441351887,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.3333333333333333
          },
          "own_lost": {
            "n": 3,
            "mean": -10.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 11477.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -1.7799167513718699
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -24.215965379392685
          }
        }
      },
      "paired_losses_both_won": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": -8.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 11312.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.7436559646940641
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -23.610178705922074
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
      }
    },
    "ring": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 37.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 143,
          "hit_units": 1022,
          "shell_damage": 13902.0,
          "own_units_hit_per_landed_enemy_shell": 7.146853146853147,
          "damage_taken_per_landed_enemy_shell": 97.21678321678321,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 20.333333333333332
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11539.0
          },
          "enemy_shells_landed": 333,
          "hit_units": 653,
          "shell_damage": 9198.0,
          "own_units_hit_per_landed_enemy_shell": 1.960960960960961,
          "damage_taken_per_landed_enemy_shell": 27.62162162162162,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -17.333333333333332
          },
          "own_dodges": {
            "n": 3,
            "mean": 11539.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -5.182869849162419
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -69.54316188197767
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -17.333333333333332
          },
          "own_dodges": {
            "n": 3,
            "mean": 11539.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -5.182869849162419
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -69.54316188197767
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
      }
    },
    "screen": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 44.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 283,
          "hit_units": 1083,
          "shell_damage": 14891.0,
          "own_units_hit_per_landed_enemy_shell": 3.8268551236749118,
          "damage_taken_per_landed_enemy_shell": 52.618374558303884,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 35.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11940.666666666666
          },
          "enemy_shells_landed": 495,
          "hit_units": 879,
          "shell_damage": 12115.0,
          "own_units_hit_per_landed_enemy_shell": 1.7757575757575759,
          "damage_taken_per_landed_enemy_shell": 24.474747474747474,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -9.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 11940.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.078557221211421
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.514230768129597
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -9.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 11940.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.078557221211421
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.514230768129597
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
      }
    },
    "storm": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 48.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 236,
          "hit_units": 818,
          "shell_damage": 11243.0,
          "own_units_hit_per_landed_enemy_shell": 3.4661016949152543,
          "damage_taken_per_landed_enemy_shell": 47.639830508474574,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 40.5
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 13085.0
          },
          "enemy_shells_landed": 390,
          "hit_units": 675,
          "shell_damage": 9304.0,
          "own_units_hit_per_landed_enemy_shell": 1.7307692307692308,
          "damage_taken_per_landed_enemy_shell": 23.856410256410257,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.5
          },
          "own_lost": {
            "n": 2,
            "mean": -8.5
          },
          "own_dodges": {
            "n": 2,
            "mean": 13085.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.7626616379310345
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -24.173017440932313
          }
        }
      },
      "paired_losses_both_won": {
        "n": 1,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 1,
            "mean": 0.0
          },
          "own_lost": {
            "n": 1,
            "mean": -3.0
          },
          "own_dodges": {
            "n": 1,
            "mean": 12527.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 1,
            "mean": -1.4403935185185186
          },
          "damage_taken_per_enemy_shell": {
            "n": 1,
            "mean": -19.633391203703702
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
      }
    },
    "swarm": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 100,
          "hit_units": 319,
          "shell_damage": 4399.0,
          "own_units_hit_per_landed_enemy_shell": 3.19,
          "damage_taken_per_landed_enemy_shell": 43.99,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 41.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 6657.0
          },
          "enemy_shells_landed": 254,
          "hit_units": 289,
          "shell_damage": 3935.0,
          "own_units_hit_per_landed_enemy_shell": 1.1377952755905512,
          "damage_taken_per_landed_enemy_shell": 15.492125984251969,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.5
          },
          "own_lost": {
            "n": 2,
            "mean": -4.5
          },
          "own_dodges": {
            "n": 2,
            "mean": 6657.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.058114053702289
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -28.519784681549385
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
        "n": 1,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 1,
            "mean": 0.0
          },
          "own_lost": {
            "n": 1,
            "mean": 0.0
          },
          "own_dodges": {
            "n": 1,
            "mean": 6446.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 1,
            "mean": -2.355723905723906
          },
          "damage_taken_per_enemy_shell": {
            "n": 1,
            "mean": -31.793771043771038
          }
        }
      }
    },
    "wedge": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 41.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 265,
          "hit_units": 1158,
          "shell_damage": 15721.0,
          "own_units_hit_per_landed_enemy_shell": 4.369811320754717,
          "damage_taken_per_landed_enemy_shell": 59.324528301886794,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 36.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 10713.666666666666
          },
          "enemy_shells_landed": 500,
          "hit_units": 870,
          "shell_damage": 11931.0,
          "own_units_hit_per_landed_enemy_shell": 1.74,
          "damage_taken_per_landed_enemy_shell": 23.862,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -5.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 10713.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.634844030325587
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -35.527050486228205
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -5.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 10713.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.634844030325587
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -35.527050486228205
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
      }
    },
    "wedge flank": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 45.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 168,
          "hit_units": 766,
          "shell_damage": 10392.0,
          "own_units_hit_per_landed_enemy_shell": 4.559523809523809,
          "damage_taken_per_landed_enemy_shell": 61.857142857142854,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 41.5
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 11398.0
          },
          "enemy_shells_landed": 354,
          "hit_units": 635,
          "shell_damage": 8660.0,
          "own_units_hit_per_landed_enemy_shell": 1.7937853107344632,
          "damage_taken_per_landed_enemy_shell": 24.463276836158194,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.5
          },
          "own_lost": {
            "n": 2,
            "mean": -6.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 11398.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.792938481866343
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -37.76511693822344
          }
        }
      },
      "paired_losses_both_won": {
        "n": 1,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 1,
            "mean": 0.0
          },
          "own_lost": {
            "n": 1,
            "mean": -4.0
          },
          "own_dodges": {
            "n": 1,
            "mean": 10266.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 1,
            "mean": -3.019197584124245
          },
          "damage_taken_per_enemy_shell": {
            "n": 1,
            "mean": -40.99431981593328
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
      }
    },
    "wedge hold": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 39.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 166,
          "hit_units": 746,
          "shell_damage": 10130.0,
          "own_units_hit_per_landed_enemy_shell": 4.493975903614458,
          "damage_taken_per_landed_enemy_shell": 61.024096385542165,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 31.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 12306.5
          },
          "enemy_shells_landed": 313,
          "hit_units": 562,
          "shell_damage": 7746.0,
          "own_units_hit_per_landed_enemy_shell": 1.7955271565495208,
          "damage_taken_per_landed_enemy_shell": 24.747603833865814,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": -8.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 12306.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.7045169682288472
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -36.35558270341696
          }
        }
      },
      "paired_losses_both_won": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": -8.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 12306.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.7045169682288472
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -36.35558270341696
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
      }
    },
    "wide line": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 3,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 344,
          "hit_units": 1198,
          "shell_damage": 16454.0,
          "own_units_hit_per_landed_enemy_shell": 3.4825581395348837,
          "damage_taken_per_landed_enemy_shell": 47.83139534883721,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 38.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11914.333333333334
          },
          "enemy_shells_landed": 511,
          "hit_units": 898,
          "shell_damage": 12365.0,
          "own_units_hit_per_landed_enemy_shell": 1.7573385518590998,
          "damage_taken_per_landed_enemy_shell": 24.19765166340509,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 1.0
          },
          "own_lost": {
            "n": 3,
            "mean": -11.333333333333334
          },
          "own_dodges": {
            "n": 3,
            "mean": 11914.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -1.7307742288918222
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -23.712572446512393
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
      }
    },
    "wolfpack": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 204,
          "hit_units": 725,
          "shell_damage": 9979.0,
          "own_units_hit_per_landed_enemy_shell": 3.553921568627451,
          "damage_taken_per_landed_enemy_shell": 48.916666666666664,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 13918.5
          },
          "enemy_shells_landed": 407,
          "hit_units": 684,
          "shell_damage": 9410.0,
          "own_units_hit_per_landed_enemy_shell": 1.6805896805896805,
          "damage_taken_per_landed_enemy_shell": 23.12039312039312,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": 0.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 13918.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.880274787347156
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -25.89462331649832
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
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": 0.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 13918.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.880274787347156
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -25.89462331649832
          }
        }
      }
    }
  }
}
```

C3 sequential look 100 paired fights (total across 20 opponents):
```json
{
  "arms": {
    "forcedP16": {
      "n": 50,
      "wins": 26,
      "own_losses_on_wins": {
        "n": 26,
        "mean": 41.92307692307692
      },
      "own_losses_on_nonwins": {
        "n": 24,
        "mean": 50.0
      },
      "dodges_per_fight": {
        "n": 50,
        "mean": 0.0
      },
      "enemy_shells_landed": 4570,
      "hit_units": 17535,
      "shell_damage": 239923.0,
      "own_units_hit_per_landed_enemy_shell": 3.836980306345733,
      "damage_taken_per_landed_enemy_shell": 52.49956236323851,
      "unassigned_enemy_artillery_damage": 0.0,
      "unresolved_enemy_shells": 19
    },
    "forcedP16+react": {
      "n": 50,
      "wins": 46,
      "own_losses_on_wins": {
        "n": 46,
        "mean": 35.28260869565217
      },
      "own_losses_on_nonwins": {
        "n": 4,
        "mean": 50.0
      },
      "dodges_per_fight": {
        "n": 50,
        "mean": 10667.18
      },
      "enemy_shells_landed": 8050,
      "hit_units": 13794,
      "shell_damage": 190096.0,
      "own_units_hit_per_landed_enemy_shell": 1.7135403726708074,
      "damage_taken_per_landed_enemy_shell": 23.614409937888198,
      "unassigned_enemy_artillery_damage": 0.0,
      "unresolved_enemy_shells": 17
    }
  },
  "paired": {
    "n": 50,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 50,
        "mean": 0.4
      },
      "own_lost": {
        "n": 50,
        "mean": -9.34
      },
      "own_dodges": {
        "n": 50,
        "mean": 10667.18
      },
      "own_units_hit_per_enemy_shell": {
        "n": 50,
        "mean": -2.2583069813350165
      },
      "damage_taken_per_enemy_shell": {
        "n": 50,
        "mean": -30.659974576684775
      }
    }
  },
  "paired_losses_both_won": {
    "n": 26,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 26,
        "mean": 0.0
      },
      "own_lost": {
        "n": 26,
        "mean": -8.576923076923077
      },
      "own_dodges": {
        "n": 26,
        "mean": 10776.076923076924
      },
      "own_units_hit_per_enemy_shell": {
        "n": 26,
        "mean": -2.709311769939266
      },
      "damage_taken_per_enemy_shell": {
        "n": 26,
        "mean": -36.57655141163986
      }
    }
  },
  "paired_losses_both_nonwin": {
    "n": 4,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 4,
        "mean": 0.0
      },
      "own_lost": {
        "n": 4,
        "mean": 0.0
      },
      "own_dodges": {
        "n": 4,
        "mean": 10369.75
      },
      "own_units_hit_per_enemy_shell": {
        "n": 4,
        "mean": -1.7863123179630276
      },
      "damage_taken_per_enemy_shell": {
        "n": 4,
        "mean": -24.34759799461091
      }
    }
  },
  "stage": "outcome",
  "look": 100,
  "complete": false,
  "declaration_sha256": "65850e8427cdc540d984ca90c278b26254a1ecbc0299fcab43796ce4e700dc6e",
  "per_tactic": {
    "alone": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 210,
          "hit_units": 638,
          "shell_damage": 8750.0,
          "own_units_hit_per_landed_enemy_shell": 3.038095238095238,
          "damage_taken_per_landed_enemy_shell": 41.666666666666664,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 22.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 6997.0
          },
          "enemy_shells_landed": 224,
          "hit_units": 432,
          "shell_damage": 5982.0,
          "own_units_hit_per_landed_enemy_shell": 1.9285714285714286,
          "damage_taken_per_landed_enemy_shell": 26.705357142857142,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 1.0
          },
          "own_lost": {
            "n": 2,
            "mean": -28.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 6997.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.0975419249533165
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -14.78782750219666
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
      }
    },
    "box": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 39.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 210,
          "hit_units": 1082,
          "shell_damage": 14659.0,
          "own_units_hit_per_landed_enemy_shell": 5.152380952380953,
          "damage_taken_per_landed_enemy_shell": 69.8047619047619,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 33.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 8659.0
          },
          "enemy_shells_landed": 421,
          "hit_units": 807,
          "shell_damage": 11105.0,
          "own_units_hit_per_landed_enemy_shell": 1.9168646080760094,
          "damage_taken_per_landed_enemy_shell": 26.377672209026127,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -6.333333333333333
          },
          "own_dodges": {
            "n": 3,
            "mean": 8659.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -3.2510847715722626
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -43.611967205166586
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -6.333333333333333
          },
          "own_dodges": {
            "n": 3,
            "mean": 8659.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -3.2510847715722626
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -43.611967205166586
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
      }
    },
    "column": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 40.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 224,
          "hit_units": 1025,
          "shell_damage": 13885.0,
          "own_units_hit_per_landed_enemy_shell": 4.575892857142857,
          "damage_taken_per_landed_enemy_shell": 61.986607142857146,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 28.333333333333332
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 9015.666666666666
          },
          "enemy_shells_landed": 373,
          "hit_units": 805,
          "shell_damage": 11127.0,
          "own_units_hit_per_landed_enemy_shell": 2.158176943699732,
          "damage_taken_per_landed_enemy_shell": 29.831099195710454,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -12.333333333333334
          },
          "own_dodges": {
            "n": 3,
            "mean": 9015.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.470853584057176
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -32.82798573541285
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -12.333333333333334
          },
          "own_dodges": {
            "n": 3,
            "mean": 9015.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.470853584057176
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -32.82798573541285
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
      }
    },
    "crescent": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 44.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 291,
          "hit_units": 1121,
          "shell_damage": 15345.0,
          "own_units_hit_per_landed_enemy_shell": 3.852233676975945,
          "damage_taken_per_landed_enemy_shell": 52.7319587628866,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 38.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 9679.666666666666
          },
          "enemy_shells_landed": 517,
          "hit_units": 902,
          "shell_damage": 12448.0,
          "own_units_hit_per_landed_enemy_shell": 1.7446808510638299,
          "damage_taken_per_landed_enemy_shell": 24.077369439071568,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.3333333333333333
          },
          "own_lost": {
            "n": 3,
            "mean": -7.666666666666667
          },
          "own_dodges": {
            "n": 3,
            "mean": 9679.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.100081076504022
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.551382820354068
          }
        }
      },
      "paired_losses_both_won": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": -6.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 9959.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.015152289602659
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -27.642529395679517
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
      }
    },
    "line": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 44.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 312,
          "hit_units": 1141,
          "shell_damage": 15637.0,
          "own_units_hit_per_landed_enemy_shell": 3.657051282051282,
          "damage_taken_per_landed_enemy_shell": 50.118589743589745,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 37.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11541.333333333334
          },
          "enemy_shells_landed": 559,
          "hit_units": 891,
          "shell_damage": 12195.0,
          "own_units_hit_per_landed_enemy_shell": 1.5939177101967799,
          "damage_taken_per_landed_enemy_shell": 21.815742397137747,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -7.333333333333333
          },
          "own_dodges": {
            "n": 3,
            "mean": 11541.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.0670787005801396
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.35761861407246
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -7.333333333333333
          },
          "own_dodges": {
            "n": 3,
            "mean": 11541.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.0670787005801396
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.35761861407246
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
      }
    },
    "line anvil": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 201,
          "hit_units": 773,
          "shell_damage": 10647.0,
          "own_units_hit_per_landed_enemy_shell": 3.845771144278607,
          "damage_taken_per_landed_enemy_shell": 52.97014925373134,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 42.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 11696.0
          },
          "enemy_shells_landed": 411,
          "hit_units": 650,
          "shell_damage": 8976.0,
          "own_units_hit_per_landed_enemy_shell": 1.5815085158150852,
          "damage_taken_per_landed_enemy_shell": 21.83941605839416,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 1.0
          },
          "own_lost": {
            "n": 2,
            "mean": -8.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 11696.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.2627753374076907
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -31.101788101604278
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
      }
    },
    "loose": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 3,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 332,
          "hit_units": 1052,
          "shell_damage": 14442.0,
          "own_units_hit_per_landed_enemy_shell": 3.1686746987951806,
          "damage_taken_per_landed_enemy_shell": 43.5,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 41.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 12063.333333333334
          },
          "enemy_shells_landed": 528,
          "hit_units": 853,
          "shell_damage": 11809.0,
          "own_units_hit_per_landed_enemy_shell": 1.615530303030303,
          "damage_taken_per_landed_enemy_shell": 22.365530303030305,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 1.0
          },
          "own_lost": {
            "n": 3,
            "mean": -8.333333333333334
          },
          "own_dodges": {
            "n": 3,
            "mean": 12063.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -1.54425769445871
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -20.99992801882351
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
      }
    },
    "loose berserk": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 196,
          "hit_units": 585,
          "shell_damage": 8084.0,
          "own_units_hit_per_landed_enemy_shell": 2.9846938775510203,
          "damage_taken_per_landed_enemy_shell": 41.244897959183675,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 40.5
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 7554.0
          },
          "enemy_shells_landed": 310,
          "hit_units": 489,
          "shell_damage": 6727.0,
          "own_units_hit_per_landed_enemy_shell": 1.5774193548387097,
          "damage_taken_per_landed_enemy_shell": 21.7,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 1.0
          },
          "own_lost": {
            "n": 2,
            "mean": -9.5
          },
          "own_dodges": {
            "n": 2,
            "mean": 7554.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.4118182267599186
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -19.600599891761377
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
      }
    },
    "loose free": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 152,
          "hit_units": 393,
          "shell_damage": 5408.0,
          "own_units_hit_per_landed_enemy_shell": 2.585526315789474,
          "damage_taken_per_landed_enemy_shell": 35.578947368421055,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 40.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 7611.0
          },
          "enemy_shells_landed": 333,
          "hit_units": 427,
          "shell_damage": 5843.0,
          "own_units_hit_per_landed_enemy_shell": 1.2822822822822824,
          "damage_taken_per_landed_enemy_shell": 17.546546546546548,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.5
          },
          "own_lost": {
            "n": 2,
            "mean": -5.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 7611.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.290461921690972
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -17.838752085902925
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
        "n": 1,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 1,
            "mean": 0.0
          },
          "own_lost": {
            "n": 1,
            "mean": 0.0
          },
          "own_dodges": {
            "n": 1,
            "mean": 7196.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 1,
            "mean": -1.028975791433892
          },
          "damage_taken_per_enemy_shell": {
            "n": 1,
            "mean": -13.807374301675978
          }
        }
      }
    },
    "loose skirmish": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 207,
          "hit_units": 740,
          "shell_damage": 10170.0,
          "own_units_hit_per_landed_enemy_shell": 3.57487922705314,
          "damage_taken_per_landed_enemy_shell": 49.130434782608695,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 36.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 12640.5
          },
          "enemy_shells_landed": 314,
          "hit_units": 515,
          "shell_damage": 7058.0,
          "own_units_hit_per_landed_enemy_shell": 1.6401273885350318,
          "damage_taken_per_landed_enemy_shell": 22.477707006369428,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 1.0
          },
          "own_lost": {
            "n": 2,
            "mean": -14.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 12640.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.9360943312847019
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -26.66947672092849
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
      }
    },
    "regular": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 44.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 326,
          "hit_units": 1150,
          "shell_damage": 15785.0,
          "own_units_hit_per_landed_enemy_shell": 3.5276073619631902,
          "damage_taken_per_landed_enemy_shell": 48.420245398773005,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 36.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11477.333333333334
          },
          "enemy_shells_landed": 503,
          "hit_units": 878,
          "shell_damage": 12162.0,
          "own_units_hit_per_landed_enemy_shell": 1.7455268389662029,
          "damage_taken_per_landed_enemy_shell": 24.178926441351887,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.3333333333333333
          },
          "own_lost": {
            "n": 3,
            "mean": -10.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 11477.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -1.7799167513718699
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -24.215965379392685
          }
        }
      },
      "paired_losses_both_won": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": -8.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 11312.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.7436559646940641
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -23.610178705922074
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
      }
    },
    "ring": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 37.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 143,
          "hit_units": 1022,
          "shell_damage": 13902.0,
          "own_units_hit_per_landed_enemy_shell": 7.146853146853147,
          "damage_taken_per_landed_enemy_shell": 97.21678321678321,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 20.333333333333332
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11539.0
          },
          "enemy_shells_landed": 333,
          "hit_units": 653,
          "shell_damage": 9198.0,
          "own_units_hit_per_landed_enemy_shell": 1.960960960960961,
          "damage_taken_per_landed_enemy_shell": 27.62162162162162,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -17.333333333333332
          },
          "own_dodges": {
            "n": 3,
            "mean": 11539.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -5.182869849162419
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -69.54316188197767
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -17.333333333333332
          },
          "own_dodges": {
            "n": 3,
            "mean": 11539.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -5.182869849162419
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -69.54316188197767
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
      }
    },
    "screen": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 44.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 283,
          "hit_units": 1083,
          "shell_damage": 14891.0,
          "own_units_hit_per_landed_enemy_shell": 3.8268551236749118,
          "damage_taken_per_landed_enemy_shell": 52.618374558303884,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 35.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11940.666666666666
          },
          "enemy_shells_landed": 495,
          "hit_units": 879,
          "shell_damage": 12115.0,
          "own_units_hit_per_landed_enemy_shell": 1.7757575757575759,
          "damage_taken_per_landed_enemy_shell": 24.474747474747474,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -9.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 11940.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.078557221211421
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.514230768129597
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -9.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 11940.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.078557221211421
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.514230768129597
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
      }
    },
    "storm": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 48.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 236,
          "hit_units": 818,
          "shell_damage": 11243.0,
          "own_units_hit_per_landed_enemy_shell": 3.4661016949152543,
          "damage_taken_per_landed_enemy_shell": 47.639830508474574,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 40.5
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 13085.0
          },
          "enemy_shells_landed": 390,
          "hit_units": 675,
          "shell_damage": 9304.0,
          "own_units_hit_per_landed_enemy_shell": 1.7307692307692308,
          "damage_taken_per_landed_enemy_shell": 23.856410256410257,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.5
          },
          "own_lost": {
            "n": 2,
            "mean": -8.5
          },
          "own_dodges": {
            "n": 2,
            "mean": 13085.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.7626616379310345
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -24.173017440932313
          }
        }
      },
      "paired_losses_both_won": {
        "n": 1,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 1,
            "mean": 0.0
          },
          "own_lost": {
            "n": 1,
            "mean": -3.0
          },
          "own_dodges": {
            "n": 1,
            "mean": 12527.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 1,
            "mean": -1.4403935185185186
          },
          "damage_taken_per_enemy_shell": {
            "n": 1,
            "mean": -19.633391203703702
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
      }
    },
    "swarm": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 100,
          "hit_units": 319,
          "shell_damage": 4399.0,
          "own_units_hit_per_landed_enemy_shell": 3.19,
          "damage_taken_per_landed_enemy_shell": 43.99,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 41.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 6657.0
          },
          "enemy_shells_landed": 254,
          "hit_units": 289,
          "shell_damage": 3935.0,
          "own_units_hit_per_landed_enemy_shell": 1.1377952755905512,
          "damage_taken_per_landed_enemy_shell": 15.492125984251969,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.5
          },
          "own_lost": {
            "n": 2,
            "mean": -4.5
          },
          "own_dodges": {
            "n": 2,
            "mean": 6657.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.058114053702289
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -28.519784681549385
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
        "n": 1,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 1,
            "mean": 0.0
          },
          "own_lost": {
            "n": 1,
            "mean": 0.0
          },
          "own_dodges": {
            "n": 1,
            "mean": 6446.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 1,
            "mean": -2.355723905723906
          },
          "damage_taken_per_enemy_shell": {
            "n": 1,
            "mean": -31.793771043771038
          }
        }
      }
    },
    "wedge": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 41.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 265,
          "hit_units": 1158,
          "shell_damage": 15721.0,
          "own_units_hit_per_landed_enemy_shell": 4.369811320754717,
          "damage_taken_per_landed_enemy_shell": 59.324528301886794,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 36.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 10713.666666666666
          },
          "enemy_shells_landed": 500,
          "hit_units": 870,
          "shell_damage": 11931.0,
          "own_units_hit_per_landed_enemy_shell": 1.74,
          "damage_taken_per_landed_enemy_shell": 23.862,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -5.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 10713.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.634844030325587
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -35.527050486228205
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -5.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 10713.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.634844030325587
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -35.527050486228205
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
      }
    },
    "wedge flank": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 45.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 168,
          "hit_units": 766,
          "shell_damage": 10392.0,
          "own_units_hit_per_landed_enemy_shell": 4.559523809523809,
          "damage_taken_per_landed_enemy_shell": 61.857142857142854,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 41.5
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 11398.0
          },
          "enemy_shells_landed": 354,
          "hit_units": 635,
          "shell_damage": 8660.0,
          "own_units_hit_per_landed_enemy_shell": 1.7937853107344632,
          "damage_taken_per_landed_enemy_shell": 24.463276836158194,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.5
          },
          "own_lost": {
            "n": 2,
            "mean": -6.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 11398.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.792938481866343
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -37.76511693822344
          }
        }
      },
      "paired_losses_both_won": {
        "n": 1,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 1,
            "mean": 0.0
          },
          "own_lost": {
            "n": 1,
            "mean": -4.0
          },
          "own_dodges": {
            "n": 1,
            "mean": 10266.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 1,
            "mean": -3.019197584124245
          },
          "damage_taken_per_enemy_shell": {
            "n": 1,
            "mean": -40.99431981593328
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
      }
    },
    "wedge hold": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 39.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 166,
          "hit_units": 746,
          "shell_damage": 10130.0,
          "own_units_hit_per_landed_enemy_shell": 4.493975903614458,
          "damage_taken_per_landed_enemy_shell": 61.024096385542165,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 31.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 12306.5
          },
          "enemy_shells_landed": 313,
          "hit_units": 562,
          "shell_damage": 7746.0,
          "own_units_hit_per_landed_enemy_shell": 1.7955271565495208,
          "damage_taken_per_landed_enemy_shell": 24.747603833865814,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": -8.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 12306.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.7045169682288472
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -36.35558270341696
          }
        }
      },
      "paired_losses_both_won": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": -8.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 12306.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.7045169682288472
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -36.35558270341696
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
      }
    },
    "wide line": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 3,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 344,
          "hit_units": 1198,
          "shell_damage": 16454.0,
          "own_units_hit_per_landed_enemy_shell": 3.4825581395348837,
          "damage_taken_per_landed_enemy_shell": 47.83139534883721,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 38.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11914.333333333334
          },
          "enemy_shells_landed": 511,
          "hit_units": 898,
          "shell_damage": 12365.0,
          "own_units_hit_per_landed_enemy_shell": 1.7573385518590998,
          "damage_taken_per_landed_enemy_shell": 24.19765166340509,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 1.0
          },
          "own_lost": {
            "n": 3,
            "mean": -11.333333333333334
          },
          "own_dodges": {
            "n": 3,
            "mean": 11914.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -1.7307742288918222
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -23.712572446512393
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
      }
    },
    "wolfpack": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 204,
          "hit_units": 725,
          "shell_damage": 9979.0,
          "own_units_hit_per_landed_enemy_shell": 3.553921568627451,
          "damage_taken_per_landed_enemy_shell": 48.916666666666664,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 13918.5
          },
          "enemy_shells_landed": 407,
          "hit_units": 684,
          "shell_damage": 9410.0,
          "own_units_hit_per_landed_enemy_shell": 1.6805896805896805,
          "damage_taken_per_landed_enemy_shell": 23.12039312039312,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": 0.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 13918.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.880274787347156
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -25.89462331649832
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
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": 0.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 13918.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.880274787347156
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -25.89462331649832
          }
        }
      }
    }
  }
}
```

C3 sequential look 200 paired fights (total across 20 opponents):
```json
{
  "arms": {
    "forcedP16": {
      "n": 50,
      "wins": 26,
      "own_losses_on_wins": {
        "n": 26,
        "mean": 41.92307692307692
      },
      "own_losses_on_nonwins": {
        "n": 24,
        "mean": 50.0
      },
      "dodges_per_fight": {
        "n": 50,
        "mean": 0.0
      },
      "enemy_shells_landed": 4570,
      "hit_units": 17535,
      "shell_damage": 239923.0,
      "own_units_hit_per_landed_enemy_shell": 3.836980306345733,
      "damage_taken_per_landed_enemy_shell": 52.49956236323851,
      "unassigned_enemy_artillery_damage": 0.0,
      "unresolved_enemy_shells": 19
    },
    "forcedP16+react": {
      "n": 50,
      "wins": 46,
      "own_losses_on_wins": {
        "n": 46,
        "mean": 35.28260869565217
      },
      "own_losses_on_nonwins": {
        "n": 4,
        "mean": 50.0
      },
      "dodges_per_fight": {
        "n": 50,
        "mean": 10667.18
      },
      "enemy_shells_landed": 8050,
      "hit_units": 13794,
      "shell_damage": 190096.0,
      "own_units_hit_per_landed_enemy_shell": 1.7135403726708074,
      "damage_taken_per_landed_enemy_shell": 23.614409937888198,
      "unassigned_enemy_artillery_damage": 0.0,
      "unresolved_enemy_shells": 17
    }
  },
  "paired": {
    "n": 50,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 50,
        "mean": 0.4
      },
      "own_lost": {
        "n": 50,
        "mean": -9.34
      },
      "own_dodges": {
        "n": 50,
        "mean": 10667.18
      },
      "own_units_hit_per_enemy_shell": {
        "n": 50,
        "mean": -2.2583069813350165
      },
      "damage_taken_per_enemy_shell": {
        "n": 50,
        "mean": -30.659974576684775
      }
    }
  },
  "paired_losses_both_won": {
    "n": 26,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 26,
        "mean": 0.0
      },
      "own_lost": {
        "n": 26,
        "mean": -8.576923076923077
      },
      "own_dodges": {
        "n": 26,
        "mean": 10776.076923076924
      },
      "own_units_hit_per_enemy_shell": {
        "n": 26,
        "mean": -2.709311769939266
      },
      "damage_taken_per_enemy_shell": {
        "n": 26,
        "mean": -36.57655141163986
      }
    }
  },
  "paired_losses_both_nonwin": {
    "n": 4,
    "unmatched_pairs": 0,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 4,
        "mean": 0.0
      },
      "own_lost": {
        "n": 4,
        "mean": 0.0
      },
      "own_dodges": {
        "n": 4,
        "mean": 10369.75
      },
      "own_units_hit_per_enemy_shell": {
        "n": 4,
        "mean": -1.7863123179630276
      },
      "damage_taken_per_enemy_shell": {
        "n": 4,
        "mean": -24.34759799461091
      }
    }
  },
  "stage": "outcome",
  "look": 200,
  "complete": false,
  "declaration_sha256": "65850e8427cdc540d984ca90c278b26254a1ecbc0299fcab43796ce4e700dc6e",
  "per_tactic": {
    "alone": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 210,
          "hit_units": 638,
          "shell_damage": 8750.0,
          "own_units_hit_per_landed_enemy_shell": 3.038095238095238,
          "damage_taken_per_landed_enemy_shell": 41.666666666666664,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 22.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 6997.0
          },
          "enemy_shells_landed": 224,
          "hit_units": 432,
          "shell_damage": 5982.0,
          "own_units_hit_per_landed_enemy_shell": 1.9285714285714286,
          "damage_taken_per_landed_enemy_shell": 26.705357142857142,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 1.0
          },
          "own_lost": {
            "n": 2,
            "mean": -28.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 6997.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.0975419249533165
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -14.78782750219666
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
      }
    },
    "box": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 39.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 210,
          "hit_units": 1082,
          "shell_damage": 14659.0,
          "own_units_hit_per_landed_enemy_shell": 5.152380952380953,
          "damage_taken_per_landed_enemy_shell": 69.8047619047619,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 33.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 8659.0
          },
          "enemy_shells_landed": 421,
          "hit_units": 807,
          "shell_damage": 11105.0,
          "own_units_hit_per_landed_enemy_shell": 1.9168646080760094,
          "damage_taken_per_landed_enemy_shell": 26.377672209026127,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -6.333333333333333
          },
          "own_dodges": {
            "n": 3,
            "mean": 8659.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -3.2510847715722626
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -43.611967205166586
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -6.333333333333333
          },
          "own_dodges": {
            "n": 3,
            "mean": 8659.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -3.2510847715722626
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -43.611967205166586
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
      }
    },
    "column": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 40.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 224,
          "hit_units": 1025,
          "shell_damage": 13885.0,
          "own_units_hit_per_landed_enemy_shell": 4.575892857142857,
          "damage_taken_per_landed_enemy_shell": 61.986607142857146,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 28.333333333333332
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 9015.666666666666
          },
          "enemy_shells_landed": 373,
          "hit_units": 805,
          "shell_damage": 11127.0,
          "own_units_hit_per_landed_enemy_shell": 2.158176943699732,
          "damage_taken_per_landed_enemy_shell": 29.831099195710454,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -12.333333333333334
          },
          "own_dodges": {
            "n": 3,
            "mean": 9015.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.470853584057176
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -32.82798573541285
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -12.333333333333334
          },
          "own_dodges": {
            "n": 3,
            "mean": 9015.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.470853584057176
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -32.82798573541285
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
      }
    },
    "crescent": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 44.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 291,
          "hit_units": 1121,
          "shell_damage": 15345.0,
          "own_units_hit_per_landed_enemy_shell": 3.852233676975945,
          "damage_taken_per_landed_enemy_shell": 52.7319587628866,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 38.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 9679.666666666666
          },
          "enemy_shells_landed": 517,
          "hit_units": 902,
          "shell_damage": 12448.0,
          "own_units_hit_per_landed_enemy_shell": 1.7446808510638299,
          "damage_taken_per_landed_enemy_shell": 24.077369439071568,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.3333333333333333
          },
          "own_lost": {
            "n": 3,
            "mean": -7.666666666666667
          },
          "own_dodges": {
            "n": 3,
            "mean": 9679.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.100081076504022
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.551382820354068
          }
        }
      },
      "paired_losses_both_won": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": -6.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 9959.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.015152289602659
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -27.642529395679517
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
      }
    },
    "line": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 44.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 312,
          "hit_units": 1141,
          "shell_damage": 15637.0,
          "own_units_hit_per_landed_enemy_shell": 3.657051282051282,
          "damage_taken_per_landed_enemy_shell": 50.118589743589745,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 37.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11541.333333333334
          },
          "enemy_shells_landed": 559,
          "hit_units": 891,
          "shell_damage": 12195.0,
          "own_units_hit_per_landed_enemy_shell": 1.5939177101967799,
          "damage_taken_per_landed_enemy_shell": 21.815742397137747,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -7.333333333333333
          },
          "own_dodges": {
            "n": 3,
            "mean": 11541.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.0670787005801396
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.35761861407246
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -7.333333333333333
          },
          "own_dodges": {
            "n": 3,
            "mean": 11541.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.0670787005801396
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.35761861407246
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
      }
    },
    "line anvil": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 201,
          "hit_units": 773,
          "shell_damage": 10647.0,
          "own_units_hit_per_landed_enemy_shell": 3.845771144278607,
          "damage_taken_per_landed_enemy_shell": 52.97014925373134,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 42.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 11696.0
          },
          "enemy_shells_landed": 411,
          "hit_units": 650,
          "shell_damage": 8976.0,
          "own_units_hit_per_landed_enemy_shell": 1.5815085158150852,
          "damage_taken_per_landed_enemy_shell": 21.83941605839416,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 1.0
          },
          "own_lost": {
            "n": 2,
            "mean": -8.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 11696.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.2627753374076907
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -31.101788101604278
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
      }
    },
    "loose": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 3,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 332,
          "hit_units": 1052,
          "shell_damage": 14442.0,
          "own_units_hit_per_landed_enemy_shell": 3.1686746987951806,
          "damage_taken_per_landed_enemy_shell": 43.5,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 41.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 12063.333333333334
          },
          "enemy_shells_landed": 528,
          "hit_units": 853,
          "shell_damage": 11809.0,
          "own_units_hit_per_landed_enemy_shell": 1.615530303030303,
          "damage_taken_per_landed_enemy_shell": 22.365530303030305,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 1.0
          },
          "own_lost": {
            "n": 3,
            "mean": -8.333333333333334
          },
          "own_dodges": {
            "n": 3,
            "mean": 12063.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -1.54425769445871
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -20.99992801882351
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
      }
    },
    "loose berserk": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 196,
          "hit_units": 585,
          "shell_damage": 8084.0,
          "own_units_hit_per_landed_enemy_shell": 2.9846938775510203,
          "damage_taken_per_landed_enemy_shell": 41.244897959183675,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 40.5
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 7554.0
          },
          "enemy_shells_landed": 310,
          "hit_units": 489,
          "shell_damage": 6727.0,
          "own_units_hit_per_landed_enemy_shell": 1.5774193548387097,
          "damage_taken_per_landed_enemy_shell": 21.7,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 1.0
          },
          "own_lost": {
            "n": 2,
            "mean": -9.5
          },
          "own_dodges": {
            "n": 2,
            "mean": 7554.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.4118182267599186
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -19.600599891761377
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
      }
    },
    "loose free": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 152,
          "hit_units": 393,
          "shell_damage": 5408.0,
          "own_units_hit_per_landed_enemy_shell": 2.585526315789474,
          "damage_taken_per_landed_enemy_shell": 35.578947368421055,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 40.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 7611.0
          },
          "enemy_shells_landed": 333,
          "hit_units": 427,
          "shell_damage": 5843.0,
          "own_units_hit_per_landed_enemy_shell": 1.2822822822822824,
          "damage_taken_per_landed_enemy_shell": 17.546546546546548,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.5
          },
          "own_lost": {
            "n": 2,
            "mean": -5.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 7611.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.290461921690972
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -17.838752085902925
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
        "n": 1,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 1,
            "mean": 0.0
          },
          "own_lost": {
            "n": 1,
            "mean": 0.0
          },
          "own_dodges": {
            "n": 1,
            "mean": 7196.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 1,
            "mean": -1.028975791433892
          },
          "damage_taken_per_enemy_shell": {
            "n": 1,
            "mean": -13.807374301675978
          }
        }
      }
    },
    "loose skirmish": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 207,
          "hit_units": 740,
          "shell_damage": 10170.0,
          "own_units_hit_per_landed_enemy_shell": 3.57487922705314,
          "damage_taken_per_landed_enemy_shell": 49.130434782608695,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 36.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 12640.5
          },
          "enemy_shells_landed": 314,
          "hit_units": 515,
          "shell_damage": 7058.0,
          "own_units_hit_per_landed_enemy_shell": 1.6401273885350318,
          "damage_taken_per_landed_enemy_shell": 22.477707006369428,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 1.0
          },
          "own_lost": {
            "n": 2,
            "mean": -14.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 12640.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.9360943312847019
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -26.66947672092849
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
      }
    },
    "regular": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 44.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 326,
          "hit_units": 1150,
          "shell_damage": 15785.0,
          "own_units_hit_per_landed_enemy_shell": 3.5276073619631902,
          "damage_taken_per_landed_enemy_shell": 48.420245398773005,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 36.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11477.333333333334
          },
          "enemy_shells_landed": 503,
          "hit_units": 878,
          "shell_damage": 12162.0,
          "own_units_hit_per_landed_enemy_shell": 1.7455268389662029,
          "damage_taken_per_landed_enemy_shell": 24.178926441351887,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.3333333333333333
          },
          "own_lost": {
            "n": 3,
            "mean": -10.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 11477.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -1.7799167513718699
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -24.215965379392685
          }
        }
      },
      "paired_losses_both_won": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": -8.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 11312.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.7436559646940641
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -23.610178705922074
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
      }
    },
    "ring": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 37.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 143,
          "hit_units": 1022,
          "shell_damage": 13902.0,
          "own_units_hit_per_landed_enemy_shell": 7.146853146853147,
          "damage_taken_per_landed_enemy_shell": 97.21678321678321,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 20.333333333333332
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11539.0
          },
          "enemy_shells_landed": 333,
          "hit_units": 653,
          "shell_damage": 9198.0,
          "own_units_hit_per_landed_enemy_shell": 1.960960960960961,
          "damage_taken_per_landed_enemy_shell": 27.62162162162162,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -17.333333333333332
          },
          "own_dodges": {
            "n": 3,
            "mean": 11539.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -5.182869849162419
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -69.54316188197767
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -17.333333333333332
          },
          "own_dodges": {
            "n": 3,
            "mean": 11539.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -5.182869849162419
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -69.54316188197767
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
      }
    },
    "screen": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 44.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 283,
          "hit_units": 1083,
          "shell_damage": 14891.0,
          "own_units_hit_per_landed_enemy_shell": 3.8268551236749118,
          "damage_taken_per_landed_enemy_shell": 52.618374558303884,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 35.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11940.666666666666
          },
          "enemy_shells_landed": 495,
          "hit_units": 879,
          "shell_damage": 12115.0,
          "own_units_hit_per_landed_enemy_shell": 1.7757575757575759,
          "damage_taken_per_landed_enemy_shell": 24.474747474747474,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -9.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 11940.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.078557221211421
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.514230768129597
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -9.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 11940.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.078557221211421
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -28.514230768129597
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
      }
    },
    "storm": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 48.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 236,
          "hit_units": 818,
          "shell_damage": 11243.0,
          "own_units_hit_per_landed_enemy_shell": 3.4661016949152543,
          "damage_taken_per_landed_enemy_shell": 47.639830508474574,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 40.5
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 13085.0
          },
          "enemy_shells_landed": 390,
          "hit_units": 675,
          "shell_damage": 9304.0,
          "own_units_hit_per_landed_enemy_shell": 1.7307692307692308,
          "damage_taken_per_landed_enemy_shell": 23.856410256410257,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.5
          },
          "own_lost": {
            "n": 2,
            "mean": -8.5
          },
          "own_dodges": {
            "n": 2,
            "mean": 13085.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.7626616379310345
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -24.173017440932313
          }
        }
      },
      "paired_losses_both_won": {
        "n": 1,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 1,
            "mean": 0.0
          },
          "own_lost": {
            "n": 1,
            "mean": -3.0
          },
          "own_dodges": {
            "n": 1,
            "mean": 12527.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 1,
            "mean": -1.4403935185185186
          },
          "damage_taken_per_enemy_shell": {
            "n": 1,
            "mean": -19.633391203703702
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
      }
    },
    "swarm": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 100,
          "hit_units": 319,
          "shell_damage": 4399.0,
          "own_units_hit_per_landed_enemy_shell": 3.19,
          "damage_taken_per_landed_enemy_shell": 43.99,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 41.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 6657.0
          },
          "enemy_shells_landed": 254,
          "hit_units": 289,
          "shell_damage": 3935.0,
          "own_units_hit_per_landed_enemy_shell": 1.1377952755905512,
          "damage_taken_per_landed_enemy_shell": 15.492125984251969,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.5
          },
          "own_lost": {
            "n": 2,
            "mean": -4.5
          },
          "own_dodges": {
            "n": 2,
            "mean": 6657.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.058114053702289
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -28.519784681549385
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
        "n": 1,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 1,
            "mean": 0.0
          },
          "own_lost": {
            "n": 1,
            "mean": 0.0
          },
          "own_dodges": {
            "n": 1,
            "mean": 6446.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 1,
            "mean": -2.355723905723906
          },
          "damage_taken_per_enemy_shell": {
            "n": 1,
            "mean": -31.793771043771038
          }
        }
      }
    },
    "wedge": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 41.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 265,
          "hit_units": 1158,
          "shell_damage": 15721.0,
          "own_units_hit_per_landed_enemy_shell": 4.369811320754717,
          "damage_taken_per_landed_enemy_shell": 59.324528301886794,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 36.333333333333336
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 10713.666666666666
          },
          "enemy_shells_landed": 500,
          "hit_units": 870,
          "shell_damage": 11931.0,
          "own_units_hit_per_landed_enemy_shell": 1.74,
          "damage_taken_per_landed_enemy_shell": 23.862,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -5.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 10713.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.634844030325587
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -35.527050486228205
          }
        }
      },
      "paired_losses_both_won": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 0.0
          },
          "own_lost": {
            "n": 3,
            "mean": -5.0
          },
          "own_dodges": {
            "n": 3,
            "mean": 10713.666666666666
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -2.634844030325587
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -35.527050486228205
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
      }
    },
    "wedge flank": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 45.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 168,
          "hit_units": 766,
          "shell_damage": 10392.0,
          "own_units_hit_per_landed_enemy_shell": 4.559523809523809,
          "damage_taken_per_landed_enemy_shell": 61.857142857142854,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 41.5
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 11398.0
          },
          "enemy_shells_landed": 354,
          "hit_units": 635,
          "shell_damage": 8660.0,
          "own_units_hit_per_landed_enemy_shell": 1.7937853107344632,
          "damage_taken_per_landed_enemy_shell": 24.463276836158194,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.5
          },
          "own_lost": {
            "n": 2,
            "mean": -6.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 11398.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.792938481866343
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -37.76511693822344
          }
        }
      },
      "paired_losses_both_won": {
        "n": 1,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 1,
            "mean": 0.0
          },
          "own_lost": {
            "n": 1,
            "mean": -4.0
          },
          "own_dodges": {
            "n": 1,
            "mean": 10266.0
          },
          "own_units_hit_per_enemy_shell": {
            "n": 1,
            "mean": -3.019197584124245
          },
          "damage_taken_per_enemy_shell": {
            "n": 1,
            "mean": -40.99431981593328
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
      }
    },
    "wedge hold": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 39.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 166,
          "hit_units": 746,
          "shell_damage": 10130.0,
          "own_units_hit_per_landed_enemy_shell": 4.493975903614458,
          "damage_taken_per_landed_enemy_shell": 61.024096385542165,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 31.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 12306.5
          },
          "enemy_shells_landed": 313,
          "hit_units": 562,
          "shell_damage": 7746.0,
          "own_units_hit_per_landed_enemy_shell": 1.7955271565495208,
          "damage_taken_per_landed_enemy_shell": 24.747603833865814,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": -8.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 12306.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.7045169682288472
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -36.35558270341696
          }
        }
      },
      "paired_losses_both_won": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": -8.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 12306.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -2.7045169682288472
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -36.35558270341696
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
      }
    },
    "wide line": {
      "arms": {
        "forcedP16": {
          "n": 3,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 3,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 344,
          "hit_units": 1198,
          "shell_damage": 16454.0,
          "own_units_hit_per_landed_enemy_shell": 3.4825581395348837,
          "damage_taken_per_landed_enemy_shell": 47.83139534883721,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        },
        "forcedP16+react": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 38.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 11914.333333333334
          },
          "enemy_shells_landed": 511,
          "hit_units": 898,
          "shell_damage": 12365.0,
          "own_units_hit_per_landed_enemy_shell": 1.7573385518590998,
          "damage_taken_per_landed_enemy_shell": 24.19765166340509,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        }
      },
      "paired": {
        "n": 3,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 3,
            "mean": 1.0
          },
          "own_lost": {
            "n": 3,
            "mean": -11.333333333333334
          },
          "own_dodges": {
            "n": 3,
            "mean": 11914.333333333334
          },
          "own_units_hit_per_enemy_shell": {
            "n": 3,
            "mean": -1.7307742288918222
          },
          "damage_taken_per_enemy_shell": {
            "n": 3,
            "mean": -23.712572446512393
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
      }
    },
    "wolfpack": {
      "arms": {
        "forcedP16": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 204,
          "hit_units": 725,
          "shell_damage": 9979.0,
          "own_units_hit_per_landed_enemy_shell": 3.553921568627451,
          "damage_taken_per_landed_enemy_shell": 48.916666666666664,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "forcedP16+react": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 13918.5
          },
          "enemy_shells_landed": 407,
          "hit_units": 684,
          "shell_damage": 9410.0,
          "own_units_hit_per_landed_enemy_shell": 1.6805896805896805,
          "damage_taken_per_landed_enemy_shell": 23.12039312039312,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        }
      },
      "paired": {
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": 0.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 13918.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.880274787347156
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -25.89462331649832
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
        "n": 2,
        "unmatched_pairs": 0,
        "direction": "forcedP16+react minus forcedP16",
        "differences": {
          "win": {
            "n": 2,
            "mean": 0.0
          },
          "own_lost": {
            "n": 2,
            "mean": 0.0
          },
          "own_dodges": {
            "n": 2,
            "mean": 13918.5
          },
          "own_units_hit_per_enemy_shell": {
            "n": 2,
            "mean": -1.880274787347156
          },
          "damage_taken_per_enemy_shell": {
            "n": 2,
            "mean": -25.89462331649832
          }
        }
      }
    }
  }
}
```

S10X: streak is primary. Ten paired series, at most ten fights each; first non-win stops that arm.
```json
{
  "complete": true,
  "primary": "streak distribution and paired streak difference",
  "series": [
    {
      "arm": "forcedP16",
      "series": 0,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "column",
          "seed": 3511481917,
          "orientation": 0,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 41
        },
        {
          "fight": 2,
          "tactic": "loose",
          "seed": 3005605140,
          "orientation": 0,
          "units_before": 9,
          "roles_before": {
            "melee": 0,
            "ranged": 0,
            "artillery": 9
          },
          "win": false,
          "own_lost": 9
        }
      ]
    },
    {
      "arm": "forcedP16",
      "series": 1,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "storm",
          "seed": 3948233975,
          "orientation": 1,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 48
        },
        {
          "fight": 2,
          "tactic": "ring",
          "seed": 977991404,
          "orientation": 1,
          "units_before": 2,
          "roles_before": {
            "melee": 0,
            "ranged": 0,
            "artillery": 2
          },
          "win": false,
          "own_lost": 2
        }
      ]
    },
    {
      "arm": "forcedP16",
      "series": 2,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "alone",
          "seed": 1622861846,
          "orientation": 0,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 42
        },
        {
          "fight": 2,
          "tactic": "line",
          "seed": 3744149061,
          "orientation": 0,
          "units_before": 8,
          "roles_before": {
            "melee": 0,
            "ranged": 0,
            "artillery": 8
          },
          "win": false,
          "own_lost": 8
        }
      ]
    },
    {
      "arm": "forcedP16",
      "series": 3,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "column",
          "seed": 1403104295,
          "orientation": 1,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 42
        },
        {
          "fight": 2,
          "tactic": "loose berserk",
          "seed": 1287461402,
          "orientation": 1,
          "units_before": 8,
          "roles_before": {
            "melee": 0,
            "ranged": 0,
            "artillery": 8
          },
          "win": false,
          "own_lost": 8
        }
      ]
    },
    {
      "arm": "forcedP16",
      "series": 4,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "column",
          "seed": 1565323603,
          "orientation": 0,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 42
        },
        {
          "fight": 2,
          "tactic": "line anvil",
          "seed": 2642252064,
          "orientation": 0,
          "units_before": 8,
          "roles_before": {
            "melee": 0,
            "ranged": 0,
            "artillery": 8
          },
          "win": false,
          "own_lost": 8
        }
      ]
    },
    {
      "arm": "forcedP16",
      "series": 5,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "box",
          "seed": 3576247087,
          "orientation": 1,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 40
        },
        {
          "fight": 2,
          "tactic": "storm",
          "seed": 518093928,
          "orientation": 1,
          "units_before": 10,
          "roles_before": {
            "melee": 0,
            "ranged": 0,
            "artillery": 10
          },
          "win": false,
          "own_lost": 10
        }
      ]
    },
    {
      "arm": "forcedP16",
      "series": 6,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "ring",
          "seed": 1382850763,
          "orientation": 0,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 40
        },
        {
          "fight": 2,
          "tactic": "line",
          "seed": 4160455379,
          "orientation": 0,
          "units_before": 10,
          "roles_before": {
            "melee": 0,
            "ranged": 0,
            "artillery": 10
          },
          "win": false,
          "own_lost": 10
        }
      ]
    },
    {
      "arm": "forcedP16",
      "series": 7,
      "complete": true,
      "streak": 0,
      "fights_reached": 1,
      "fights": [
        {
          "fight": 1,
          "tactic": "storm",
          "seed": 442865731,
          "orientation": 1,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": false,
          "own_lost": 50
        }
      ]
    },
    {
      "arm": "forcedP16",
      "series": 8,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "wedge flank",
          "seed": 2454414419,
          "orientation": 0,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 46
        },
        {
          "fight": 2,
          "tactic": "screen",
          "seed": 3380158170,
          "orientation": 0,
          "units_before": 4,
          "roles_before": {
            "melee": 0,
            "ranged": 0,
            "artillery": 4
          },
          "win": false,
          "own_lost": 4
        }
      ]
    },
    {
      "arm": "forcedP16",
      "series": 9,
      "complete": true,
      "streak": 0,
      "fights_reached": 1,
      "fights": [
        {
          "fight": 1,
          "tactic": "loose free",
          "seed": 1109178398,
          "orientation": 1,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": false,
          "own_lost": 50
        }
      ]
    },
    {
      "arm": "forcedP16+react",
      "series": 0,
      "complete": true,
      "streak": 2,
      "fights_reached": 3,
      "fights": [
        {
          "fight": 1,
          "tactic": "column",
          "seed": 3511481917,
          "orientation": 0,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 14
        },
        {
          "fight": 2,
          "tactic": "loose",
          "seed": 3005605140,
          "orientation": 0,
          "units_before": 36,
          "roles_before": {
            "melee": 5,
            "ranged": 21,
            "artillery": 10
          },
          "win": true,
          "own_lost": 32
        },
        {
          "fight": 3,
          "tactic": "wolfpack",
          "seed": 544205302,
          "orientation": 0,
          "units_before": 4,
          "roles_before": {
            "melee": 0,
            "ranged": 0,
            "artillery": 4
          },
          "win": false,
          "own_lost": 4
        }
      ]
    },
    {
      "arm": "forcedP16+react",
      "series": 1,
      "complete": true,
      "streak": 2,
      "fights_reached": 3,
      "fights": [
        {
          "fight": 1,
          "tactic": "storm",
          "seed": 3948233975,
          "orientation": 1,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 34
        },
        {
          "fight": 2,
          "tactic": "ring",
          "seed": 977991404,
          "orientation": 1,
          "units_before": 16,
          "roles_before": {
            "melee": 1,
            "ranged": 5,
            "artillery": 10
          },
          "win": true,
          "own_lost": 6
        },
        {
          "fight": 3,
          "tactic": "storm",
          "seed": 3049569543,
          "orientation": 1,
          "units_before": 10,
          "roles_before": {
            "melee": 0,
            "ranged": 0,
            "artillery": 10
          },
          "win": false,
          "own_lost": 10
        }
      ]
    },
    {
      "arm": "forcedP16+react",
      "series": 2,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "alone",
          "seed": 1622861846,
          "orientation": 0,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 21
        },
        {
          "fight": 2,
          "tactic": "line",
          "seed": 3744149061,
          "orientation": 0,
          "units_before": 29,
          "roles_before": {
            "melee": 0,
            "ranged": 19,
            "artillery": 10
          },
          "win": false,
          "own_lost": 29
        }
      ]
    },
    {
      "arm": "forcedP16+react",
      "series": 3,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "column",
          "seed": 1403104295,
          "orientation": 1,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 25
        },
        {
          "fight": 2,
          "tactic": "loose berserk",
          "seed": 1287461402,
          "orientation": 1,
          "units_before": 25,
          "roles_before": {
            "melee": 2,
            "ranged": 13,
            "artillery": 10
          },
          "win": false,
          "own_lost": 25
        }
      ]
    },
    {
      "arm": "forcedP16+react",
      "series": 4,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "column",
          "seed": 1565323603,
          "orientation": 0,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 22
        },
        {
          "fight": 2,
          "tactic": "line anvil",
          "seed": 2642252064,
          "orientation": 0,
          "units_before": 28,
          "roles_before": {
            "melee": 1,
            "ranged": 17,
            "artillery": 10
          },
          "win": false,
          "own_lost": 28
        }
      ]
    },
    {
      "arm": "forcedP16+react",
      "series": 5,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "box",
          "seed": 3576247087,
          "orientation": 1,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 31
        },
        {
          "fight": 2,
          "tactic": "storm",
          "seed": 518093928,
          "orientation": 1,
          "units_before": 19,
          "roles_before": {
            "melee": 0,
            "ranged": 9,
            "artillery": 10
          },
          "win": false,
          "own_lost": 19
        }
      ]
    },
    {
      "arm": "forcedP16+react",
      "series": 6,
      "complete": true,
      "streak": 2,
      "fights_reached": 3,
      "fights": [
        {
          "fight": 1,
          "tactic": "ring",
          "seed": 1382850763,
          "orientation": 0,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 16
        },
        {
          "fight": 2,
          "tactic": "line",
          "seed": 4160455379,
          "orientation": 0,
          "units_before": 34,
          "roles_before": {
            "melee": 3,
            "ranged": 21,
            "artillery": 10
          },
          "win": true,
          "own_lost": 25
        },
        {
          "fight": 3,
          "tactic": "wolfpack",
          "seed": 4198109992,
          "orientation": 0,
          "units_before": 9,
          "roles_before": {
            "melee": 0,
            "ranged": 0,
            "artillery": 9
          },
          "win": false,
          "own_lost": 9
        }
      ]
    },
    {
      "arm": "forcedP16+react",
      "series": 7,
      "complete": true,
      "streak": 2,
      "fights_reached": 3,
      "fights": [
        {
          "fight": 1,
          "tactic": "storm",
          "seed": 442865731,
          "orientation": 1,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 36
        },
        {
          "fight": 2,
          "tactic": "column",
          "seed": 3483282947,
          "orientation": 1,
          "units_before": 14,
          "roles_before": {
            "melee": 1,
            "ranged": 3,
            "artillery": 10
          },
          "win": true,
          "own_lost": 10
        },
        {
          "fight": 3,
          "tactic": "loose skirmish",
          "seed": 2903716547,
          "orientation": 1,
          "units_before": 4,
          "roles_before": {
            "melee": 0,
            "ranged": 0,
            "artillery": 4
          },
          "win": false,
          "own_lost": 4
        }
      ]
    },
    {
      "arm": "forcedP16+react",
      "series": 8,
      "complete": true,
      "streak": 1,
      "fights_reached": 2,
      "fights": [
        {
          "fight": 1,
          "tactic": "wedge flank",
          "seed": 2454414419,
          "orientation": 0,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": true,
          "own_lost": 31
        },
        {
          "fight": 2,
          "tactic": "screen",
          "seed": 3380158170,
          "orientation": 0,
          "units_before": 19,
          "roles_before": {
            "melee": 0,
            "ranged": 9,
            "artillery": 10
          },
          "win": false,
          "own_lost": 19
        }
      ]
    },
    {
      "arm": "forcedP16+react",
      "series": 9,
      "complete": true,
      "streak": 0,
      "fights_reached": 1,
      "fights": [
        {
          "fight": 1,
          "tactic": "loose free",
          "seed": 1109178398,
          "orientation": 1,
          "units_before": 50,
          "roles_before": {
            "melee": 10,
            "ranged": 30,
            "artillery": 10
          },
          "win": false,
          "own_lost": 50
        }
      ]
    }
  ],
  "arms": {
    "forcedP16": {
      "n_series": 10,
      "streak_distribution": {
        "1": 8,
        "0": 2
      },
      "mean_streak": {
        "n": 10,
        "mean": 0.8
      },
      "reach": [
        {
          "fight": 1,
          "n": 10,
          "denominator": 10,
          "units_before": {
            "n": 10,
            "mean": 50.0
          },
          "role_units_before": {
            "melee": {
              "n": 10,
              "mean": 10.0
            },
            "ranged": {
              "n": 10,
              "mean": 30.0
            },
            "artillery": {
              "n": 10,
              "mean": 10.0
            }
          }
        },
        {
          "fight": 2,
          "n": 8,
          "denominator": 10,
          "units_before": {
            "n": 8,
            "mean": 7.375
          },
          "role_units_before": {
            "melee": {
              "n": 8,
              "mean": 0.0
            },
            "ranged": {
              "n": 8,
              "mean": 0.0
            },
            "artillery": {
              "n": 8,
              "mean": 7.375
            }
          }
        },
        {
          "fight": 3,
          "n": 0,
          "denominator": 10,
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
          "denominator": 10,
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
          "denominator": 10,
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
          "denominator": 10,
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
          "denominator": 10,
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
          "denominator": 10,
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
          "denominator": 10,
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
          "denominator": 10,
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
        "n": 18,
        "wins": 8,
        "own_losses_on_wins": {
          "n": 8,
          "mean": 42.625
        },
        "own_losses_on_nonwins": {
          "n": 10,
          "mean": 15.9
        },
        "dodges_per_fight": {
          "n": 18,
          "mean": 0.0
        },
        "enemy_shells_landed": 1114,
        "hit_units": 3713,
        "shell_damage": 50902.0,
        "own_units_hit_per_landed_enemy_shell": 3.3330341113105924,
        "damage_taken_per_landed_enemy_shell": 45.692998204667866,
        "unassigned_enemy_artillery_damage": 0.0,
        "unresolved_enemy_shells": 19
      },
      "per_tactic": {
        "alone": {
          "n": 1,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 42.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 0.0
          },
          "enemy_shells_landed": 95,
          "hit_units": 332,
          "shell_damage": 4517.0,
          "own_units_hit_per_landed_enemy_shell": 3.4947368421052634,
          "damage_taken_per_landed_enemy_shell": 47.54736842105263,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "box": {
          "n": 1,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 40.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 0.0
          },
          "enemy_shells_landed": 57,
          "hit_units": 337,
          "shell_damage": 4615.0,
          "own_units_hit_per_landed_enemy_shell": 5.912280701754386,
          "damage_taken_per_landed_enemy_shell": 80.96491228070175,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "column": {
          "n": 3,
          "wins": 3,
          "own_losses_on_wins": {
            "n": 3,
            "mean": 41.666666666666664
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 227,
          "hit_units": 1027,
          "shell_damage": 13833.0,
          "own_units_hit_per_landed_enemy_shell": 4.524229074889868,
          "damage_taken_per_landed_enemy_shell": 60.93832599118943,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "line": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 9.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 102,
          "hit_units": 155,
          "shell_damage": 2231.0,
          "own_units_hit_per_landed_enemy_shell": 1.5196078431372548,
          "damage_taken_per_landed_enemy_shell": 21.872549019607842,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 6
        },
        "line anvil": {
          "n": 1,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 8.0
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 0.0
          },
          "enemy_shells_landed": 47,
          "hit_units": 60,
          "shell_damage": 857.0,
          "own_units_hit_per_landed_enemy_shell": 1.2765957446808511,
          "damage_taken_per_landed_enemy_shell": 18.23404255319149,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 5
        },
        "loose": {
          "n": 1,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 9.0
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 0.0
          },
          "enemy_shells_landed": 46,
          "hit_units": 52,
          "shell_damage": 730.0,
          "own_units_hit_per_landed_enemy_shell": 1.1304347826086956,
          "damage_taken_per_landed_enemy_shell": 15.869565217391305,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "loose berserk": {
          "n": 1,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 8.0
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 0.0
          },
          "enemy_shells_landed": 34,
          "hit_units": 42,
          "shell_damage": 621.0,
          "own_units_hit_per_landed_enemy_shell": 1.2352941176470589,
          "damage_taken_per_landed_enemy_shell": 18.264705882352942,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "loose free": {
          "n": 1,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 0.0
          },
          "enemy_shells_landed": 69,
          "hit_units": 125,
          "shell_damage": 1755.0,
          "own_units_hit_per_landed_enemy_shell": 1.8115942028985508,
          "damage_taken_per_landed_enemy_shell": 25.434782608695652,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "ring": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 40.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 2.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 0.0
          },
          "enemy_shells_landed": 64,
          "hit_units": 361,
          "shell_damage": 4961.0,
          "own_units_hit_per_landed_enemy_shell": 5.640625,
          "damage_taken_per_landed_enemy_shell": 77.515625,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "screen": {
          "n": 1,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 4.0
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 0.0
          },
          "enemy_shells_landed": 39,
          "hit_units": 35,
          "shell_damage": 502.0,
          "own_units_hit_per_landed_enemy_shell": 0.8974358974358975,
          "damage_taken_per_landed_enemy_shell": 12.871794871794872,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        },
        "storm": {
          "n": 3,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 48.0
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 30.0
          },
          "dodges_per_fight": {
            "n": 3,
            "mean": 0.0
          },
          "enemy_shells_landed": 236,
          "hit_units": 815,
          "shell_damage": 11252.0,
          "own_units_hit_per_landed_enemy_shell": 3.4533898305084745,
          "damage_taken_per_landed_enemy_shell": 47.67796610169491,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        },
        "wedge flank": {
          "n": 1,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 46.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 0.0
          },
          "enemy_shells_landed": 98,
          "hit_units": 372,
          "shell_damage": 5028.0,
          "own_units_hit_per_landed_enemy_shell": 3.795918367346939,
          "damage_taken_per_landed_enemy_shell": 51.30612244897959,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        }
      }
    },
    "forcedP16+react": {
      "n_series": 10,
      "streak_distribution": {
        "2": 4,
        "1": 5,
        "0": 1
      },
      "mean_streak": {
        "n": 10,
        "mean": 1.3
      },
      "reach": [
        {
          "fight": 1,
          "n": 10,
          "denominator": 10,
          "units_before": {
            "n": 10,
            "mean": 50.0
          },
          "role_units_before": {
            "melee": {
              "n": 10,
              "mean": 10.0
            },
            "ranged": {
              "n": 10,
              "mean": 30.0
            },
            "artillery": {
              "n": 10,
              "mean": 10.0
            }
          }
        },
        {
          "fight": 2,
          "n": 9,
          "denominator": 10,
          "units_before": {
            "n": 9,
            "mean": 24.444444444444443
          },
          "role_units_before": {
            "melee": {
              "n": 9,
              "mean": 1.4444444444444444
            },
            "ranged": {
              "n": 9,
              "mean": 13.0
            },
            "artillery": {
              "n": 9,
              "mean": 10.0
            }
          }
        },
        {
          "fight": 3,
          "n": 4,
          "denominator": 10,
          "units_before": {
            "n": 4,
            "mean": 6.75
          },
          "role_units_before": {
            "melee": {
              "n": 4,
              "mean": 0.0
            },
            "ranged": {
              "n": 4,
              "mean": 0.0
            },
            "artillery": {
              "n": 4,
              "mean": 6.75
            }
          }
        },
        {
          "fight": 4,
          "n": 0,
          "denominator": 10,
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
          "denominator": 10,
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
          "denominator": 10,
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
          "denominator": 10,
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
          "denominator": 10,
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
          "denominator": 10,
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
          "denominator": 10,
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
        "n": 23,
        "wins": 13,
        "own_losses_on_wins": {
          "n": 13,
          "mean": 23.307692307692307
        },
        "own_losses_on_nonwins": {
          "n": 10,
          "mean": 19.7
        },
        "dodges_per_fight": {
          "n": 23,
          "mean": 5946.608695652174
        },
        "enemy_shells_landed": 2606,
        "hit_units": 3918,
        "shell_damage": 54410.0,
        "own_units_hit_per_landed_enemy_shell": 1.5034535686876438,
        "damage_taken_per_landed_enemy_shell": 20.87874136607828,
        "unassigned_enemy_artillery_damage": 0.0,
        "unresolved_enemy_shells": 18
      },
      "per_tactic": {
        "alone": {
          "n": 1,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 21.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 5581.0
          },
          "enemy_shells_landed": 98,
          "hit_units": 232,
          "shell_damage": 3206.0,
          "own_units_hit_per_landed_enemy_shell": 2.36734693877551,
          "damage_taken_per_landed_enemy_shell": 32.714285714285715,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "box": {
          "n": 1,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 31.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 11037.0
          },
          "enemy_shells_landed": 138,
          "hit_units": 262,
          "shell_damage": 3597.0,
          "own_units_hit_per_landed_enemy_shell": 1.8985507246376812,
          "damage_taken_per_landed_enemy_shell": 26.065217391304348,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        },
        "column": {
          "n": 4,
          "wins": 4,
          "own_losses_on_wins": {
            "n": 4,
            "mean": 17.75
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 4,
            "mean": 8020.0
          },
          "enemy_shells_landed": 461,
          "hit_units": 826,
          "shell_damage": 11548.0,
          "own_units_hit_per_landed_enemy_shell": 1.79175704989154,
          "damage_taken_per_landed_enemy_shell": 25.04989154013015,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "line": {
          "n": 2,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 25.0
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 29.0
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 5443.0
          },
          "enemy_shells_landed": 315,
          "hit_units": 394,
          "shell_damage": 5532.0,
          "own_units_hit_per_landed_enemy_shell": 1.2507936507936508,
          "damage_taken_per_landed_enemy_shell": 17.561904761904763,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "line anvil": {
          "n": 1,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 28.0
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 4910.0
          },
          "enemy_shells_landed": 153,
          "hit_units": 204,
          "shell_damage": 2841.0,
          "own_units_hit_per_landed_enemy_shell": 1.3333333333333333,
          "damage_taken_per_landed_enemy_shell": 18.568627450980394,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "loose": {
          "n": 1,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 32.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 7621.0
          },
          "enemy_shells_landed": 185,
          "hit_units": 216,
          "shell_damage": 2983.0,
          "own_units_hit_per_landed_enemy_shell": 1.1675675675675676,
          "damage_taken_per_landed_enemy_shell": 16.124324324324323,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "loose berserk": {
          "n": 1,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 25.0
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 4193.0
          },
          "enemy_shells_landed": 109,
          "hit_units": 136,
          "shell_damage": 1898.0,
          "own_units_hit_per_landed_enemy_shell": 1.2477064220183487,
          "damage_taken_per_landed_enemy_shell": 17.412844036697248,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        },
        "loose free": {
          "n": 1,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 50.0
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 4178.0
          },
          "enemy_shells_landed": 161,
          "hit_units": 203,
          "shell_damage": 2801.0,
          "own_units_hit_per_landed_enemy_shell": 1.2608695652173914,
          "damage_taken_per_landed_enemy_shell": 17.39751552795031,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 2
        },
        "loose skirmish": {
          "n": 1,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 4.0
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 726.0
          },
          "enemy_shells_landed": 32,
          "hit_units": 33,
          "shell_damage": 468.0,
          "own_units_hit_per_landed_enemy_shell": 1.03125,
          "damage_taken_per_landed_enemy_shell": 14.625,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        },
        "ring": {
          "n": 2,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 11.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 5942.0
          },
          "enemy_shells_landed": 167,
          "hit_units": 276,
          "shell_damage": 3871.0,
          "own_units_hit_per_landed_enemy_shell": 1.652694610778443,
          "damage_taken_per_landed_enemy_shell": 23.179640718562876,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 0
        },
        "screen": {
          "n": 1,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 1,
            "mean": 19.0
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 2553.0
          },
          "enemy_shells_landed": 144,
          "hit_units": 144,
          "shell_damage": 1969.0,
          "own_units_hit_per_landed_enemy_shell": 1.0,
          "damage_taken_per_landed_enemy_shell": 13.67361111111111,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        },
        "storm": {
          "n": 4,
          "wins": 2,
          "own_losses_on_wins": {
            "n": 2,
            "mean": 35.0
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 14.5
          },
          "dodges_per_fight": {
            "n": 4,
            "mean": 6653.25
          },
          "enemy_shells_landed": 412,
          "hit_units": 643,
          "shell_damage": 8844.0,
          "own_units_hit_per_landed_enemy_shell": 1.5606796116504855,
          "damage_taken_per_landed_enemy_shell": 21.466019417475728,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 3
        },
        "wedge flank": {
          "n": 1,
          "wins": 1,
          "own_losses_on_wins": {
            "n": 1,
            "mean": 31.0
          },
          "own_losses_on_nonwins": {
            "n": 0,
            "mean": null
          },
          "dodges_per_fight": {
            "n": 1,
            "mean": 12664.0
          },
          "enemy_shells_landed": 154,
          "hit_units": 271,
          "shell_damage": 3702.0,
          "own_units_hit_per_landed_enemy_shell": 1.7597402597402598,
          "damage_taken_per_landed_enemy_shell": 24.038961038961038,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 1
        },
        "wolfpack": {
          "n": 2,
          "wins": 0,
          "own_losses_on_wins": {
            "n": 0,
            "mean": null
          },
          "own_losses_on_nonwins": {
            "n": 2,
            "mean": 6.5
          },
          "dodges_per_fight": {
            "n": 2,
            "mean": 923.0
          },
          "enemy_shells_landed": 77,
          "hit_units": 78,
          "shell_damage": 1150.0,
          "own_units_hit_per_landed_enemy_shell": 1.0129870129870129,
          "damage_taken_per_landed_enemy_shell": 14.935064935064934,
          "unassigned_enemy_artillery_damage": 0.0,
          "unresolved_enemy_shells": 4
        }
      }
    }
  },
  "paired_streak_difference": {
    "direction": "react minus base",
    "n": 10,
    "mean": 0.5
  },
  "paired_reached_fights": {
    "n": 18,
    "unmatched_pairs": 5,
    "direction": "forcedP16+react minus forcedP16",
    "differences": {
      "win": {
        "n": 18,
        "mean": 0.2222222222222222
      },
      "own_lost": {
        "n": 18,
        "mean": -2.0555555555555554
      },
      "own_dodges": {
        "n": 18,
        "mean": 7287.444444444444
      },
      "own_units_hit_per_enemy_shell": {
        "n": 18,
        "mean": -1.4472773600708517
      },
      "damage_taken_per_enemy_shell": {
        "n": 18,
        "mean": -19.834859048679945
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
