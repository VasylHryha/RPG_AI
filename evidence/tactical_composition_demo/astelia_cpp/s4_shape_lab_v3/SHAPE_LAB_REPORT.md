DONE

# Shape lab v2: development tooling and observations

Implements SHAPE_LAB_SPEC §§3–6. No judging seeds, registered endpoints, policy changes or scientific acceptance.
V2 uses fresh development entropy and the unchanged v1 native engine/checks. V1 evidence is preserved.

## Section-3 checks

| Check | Result |
|---|---|
| 50v50 entire output byte equality | PASS |
| dummy_static no damage/no launches/no movement | PASS |
| dummy_static_fire attacks and never moves | PASS |
| dummy_advance catalog speed, gun pursuit, fire contract | PASS |
| dummy_advance_fire catalog speed, gun pursuit, fire contract | PASS |
| static body stays fixed under collision | PASS |
| placement deterministic and first role slots | PASS |
| carry-over heals survivors, dead stay absent | PASS |

Compatibility output stream SHA256: `336df649bbe1409b63fa5429737fdb0a6f8b3698e44074b110bc3dac555f9e75`.
Measured full-output compatibility fight: 18.266 seconds.

Required check receipt status: PASS

## Projection and process gate

```json
{
  "status": "MEASURED",
  "workers": 6,
  "declaration_sha256": "ab5bcf6eb0bb0ef4fef0c0575e38feb948d9ff1f4900317ac54aef21efc6bdd7",
  "attempt_hashes": {
    "CALIBRATE_ATTEMPT_301b2e96b6ffd20f.json": "2db1d6c83c720fcad4daa5089be453b8858722bb1c1acf74c9c68096268cc2fb"
  },
  "sample_tags": [
    "D1_v7_p00_c0_o0",
    "D1_forcedP16_p00_c0_o0",
    "D2_v7_p00_c0_o0",
    "D2_forcedP16_p00_c0_o0",
    "D3_v7_p00_c0_o0",
    "D3_forcedP16_p00_c0_o0",
    "D4_v7_p00_c0_o0",
    "D4_forcedP16_p00_c0_o0",
    "D4_v6_p00_c0_o0",
    "D5_v7_p00_c0_o0",
    "D5_forcedP16_p00_c0_o0",
    "D5_v6_p00_c0_o0",
    "C1_v7_p00_c0_o0",
    "C1_forcedP16_p00_c0_o0",
    "C2_v7_p00_c0_o0",
    "C2_forcedP16_p00_c0_o0",
    "C3_v7_p00_c0_o0",
    "C3_v7_p01_c0_o0",
    "C3_v7_p02_c0_o0",
    "C3_v7_p03_c0_o0",
    "C3_v7_p04_c0_o0",
    "C3_v7_p05_c0_o0",
    "C3_v7_p06_c0_o0",
    "C3_v7_p07_c0_o0",
    "C3_v7_p08_c0_o0",
    "C3_v7_p09_c0_o0",
    "C3_v7_p10_c0_o0",
    "C3_v7_p11_c0_o0",
    "C3_v7_p12_c0_o0",
    "C3_v7_p13_c0_o0",
    "C3_v7_p14_c0_o0",
    "C3_v7_p15_c0_o0",
    "C3_v7_p16_c0_o0",
    "C3_v7_p17_c0_o0",
    "C3_v7_p18_c0_o0",
    "C3_v7_p19_c0_o0",
    "C3_forcedP16_p00_c0_o0",
    "C3_forcedP16_p01_c0_o0",
    "C3_forcedP16_p02_c0_o0",
    "C3_forcedP16_p03_c0_o0",
    "C3_forcedP16_p04_c0_o0",
    "C3_forcedP16_p05_c0_o0",
    "C3_forcedP16_p06_c0_o0",
    "C3_forcedP16_p07_c0_o0",
    "C3_forcedP16_p08_c0_o0",
    "C3_forcedP16_p09_c0_o0",
    "C3_forcedP16_p10_c0_o0",
    "C3_forcedP16_p11_c0_o0",
    "C3_forcedP16_p12_c0_o0",
    "C3_forcedP16_p13_c0_o0",
    "C3_forcedP16_p14_c0_o0",
    "C3_forcedP16_p15_c0_o0",
    "C3_forcedP16_p16_c0_o0",
    "C3_forcedP16_p17_c0_o0",
    "C3_forcedP16_p18_c0_o0",
    "C3_forcedP16_p19_c0_o0",
    "S10X_v7_s00_f01",
    "S10X_forcedP16_s00_f01",
    "S10X_elite_s00_f01"
  ],
  "sample_receipt_hashes": {
    "D1_v7_p00_c0_o0": "87213ea6c03d8b53f1a73cf13e8f24e7d006d2ecd6d505c4dffe95479f54406d",
    "D1_forcedP16_p00_c0_o0": "e18d702ef7e5e655cfc11b9d8f20fab3e87df37df16f2a9d989a5b1f14f9ba9c",
    "D2_v7_p00_c0_o0": "21184fa86a9e22281ad5981f796e76f703ccba1e5b0cdd3f48b10f2b86a761f9",
    "D2_forcedP16_p00_c0_o0": "6f5962662480d1b338a3fdab924b08e35638fecc61a7492a5185dbfdb3b79008",
    "D3_v7_p00_c0_o0": "986df17aaac3bba4c6228e6eae21e05561c0a8f1b8cc1f69947e81e37049323d",
    "D3_forcedP16_p00_c0_o0": "a72d0ab13e53c2dd9e042a6213539892dcb08ab19f1ee7a400d35df9d64db1e2",
    "D4_v7_p00_c0_o0": "4f1ecd52024f7d977970f35168a40b9db97be210bb0c21f43c6d7eb50e04b4d1",
    "D4_forcedP16_p00_c0_o0": "e014357fef2725718ebd34f5d9aca0ed50becd0a7446dcb51af79ce51b890e8c",
    "D4_v6_p00_c0_o0": "ec5caf0e61dc405348876939da26ce11da01af65f15bbebb06a74474484a1265",
    "D5_v7_p00_c0_o0": "87b0a4dc81afbbd3291fadede5b6261ff368a1bce1d3f8c169ef23a3ff5141c8",
    "D5_forcedP16_p00_c0_o0": "f3ea4ccf5c2f03b602f8d82da97c06b36b1cd1d45e65f483f02ed9dc9d683499",
    "D5_v6_p00_c0_o0": "23ee8e492b94670e4a4aca200feee573167f1afbec7d19e10b3ceac9b8579dc8",
    "C1_v7_p00_c0_o0": "43a927cc3f4ef139128349f3b30ffdd18766629e4fc9ab2fcc6bd9dee9eb4b6a",
    "C1_forcedP16_p00_c0_o0": "837f2f7259e3c6587e0280bf1a391fd9fa947b0f6453e633be75f74ea87e3c8c",
    "C2_v7_p00_c0_o0": "b5efffd37fd7ba1a5675895f65d23e8637c99468becb4bf2e8de6a70f476d63c",
    "C2_forcedP16_p00_c0_o0": "c422f88d6905458b238d98656854473ecb5be0f2f1ca6c63e3ca65e74f733cc4",
    "C3_v7_p00_c0_o0": "7f3030e4c0efc1b07c60edeeb099998226d2c9996c669b474e5a010dcbe91794",
    "C3_v7_p01_c0_o0": "f65b61fbd01c054ea0355350b564ec0444569e2332520db257a3f2c3789de311",
    "C3_v7_p02_c0_o0": "9c1613df5377268a92d7b75b1aa21ca97bdc3fa8e84147cb8fb935100cef5d31",
    "C3_v7_p03_c0_o0": "d0a9e4ebc5e6ccca9375b349ff22083df2ae83f6bc9df9baa12a7f2550a0b45f",
    "C3_v7_p04_c0_o0": "933d2be29a748183c813579ad51dfe4288866b99dfc97340c0ce25243a1ca337",
    "C3_v7_p05_c0_o0": "057eb796975d4e2004cb9ec5bc3ba98998e349f776ed4d76e67310072f5c3d51",
    "C3_v7_p06_c0_o0": "df2675c094cacfcb57f0b516b0d3e301d23dc12dfd0f82c3d293c73b86bbd7e2",
    "C3_v7_p07_c0_o0": "f3235c076486adc4932955afdbdfc2d25ba90f1921e52e23ac546e2d5f0af256",
    "C3_v7_p08_c0_o0": "5c6be9cb0dbcf4418e007a45d48dc912881df4f032609982aacce5b971bc4ff4",
    "C3_v7_p09_c0_o0": "34f865be51d86757a603d5ecd3cf746efa9310fd3b2bd19ce7a7bd21a20cb262",
    "C3_v7_p10_c0_o0": "716a96562068709adc2cd8f124be3704d1aaa726b5b342b4a513867bd3f26157",
    "C3_v7_p11_c0_o0": "9a200f0a000e377b4c74a40166f827c9f14b99e4e3c9dc7fafc5d79ad17b28c3",
    "C3_v7_p12_c0_o0": "b7b3c7800d78a8156ccb2364800fde908105fd2c810178b795be498b7e4309e3",
    "C3_v7_p13_c0_o0": "790579374b773c2d3b4de6df81ef887c011062299003c0652e2ec69379d0ce75",
    "C3_v7_p14_c0_o0": "a9db52a49c95bd7f6339c9ddc1d076e73001552e7bfadff326c819fe2f655062",
    "C3_v7_p15_c0_o0": "78f7e48d7be130b86ebec396b36bb4d533604cfe8a61c79e741d00d0de849be8",
    "C3_v7_p16_c0_o0": "6f0d6f72d4093fcdbd37d3d610c37875fd3c27173460dd47103c22041e8530b1",
    "C3_v7_p17_c0_o0": "4268a1f18879b0784cc659711a68af27f2323c8242386bacbffbb96a91d101f4",
    "C3_v7_p18_c0_o0": "ea8e346ee59953c4e800c5d7b91ede437bd3dfcb9963d9382917646d08c97fd3",
    "C3_v7_p19_c0_o0": "2c77fab45e159d52e7bbf41f1b02e53fd9fbe580d5ed8969e9c97278a4e027b8",
    "C3_forcedP16_p00_c0_o0": "9796bd66c1fec8ae928462e44cb070f617b36f7b2357fc67ddfd7ada32e2c51e",
    "C3_forcedP16_p01_c0_o0": "4e818a61c02e79c6fde7a5615938712a0ad08eebddc0bb1db21e1189583114a7",
    "C3_forcedP16_p02_c0_o0": "37be91988ca7070069a8c590b62aed89662a7be129b3775e516e00d4e3848fae",
    "C3_forcedP16_p03_c0_o0": "35bd02007bb523b5ede47131846aa29ee1c9aaea77376b298ff6c07c7705c095",
    "C3_forcedP16_p04_c0_o0": "afe7eff6e4425c9931d8c282215698b6f5c88251c2690313efc3efcf383bd500",
    "C3_forcedP16_p05_c0_o0": "00fd8ab42235c787ba2d6aade890e5826dc76ecfe40ee288914f82bc385bbcc7",
    "C3_forcedP16_p06_c0_o0": "a2fa5ce7c730f014bb505aa3849f04836ec95706888c7024c9f2007ac3fddc97",
    "C3_forcedP16_p07_c0_o0": "d04eb833966e04ce0b7832af7140c4482d44c923eb326abee80f7e77b9ba9684",
    "C3_forcedP16_p08_c0_o0": "df2650d90ce03cdb01fb902e70c01d313c9dd71e97855e476e7e3c051af72ea0",
    "C3_forcedP16_p09_c0_o0": "84501eaaee06aaf0c28cc0a2ecca8c995e42d632987a32bed67e3f6a7d75a76b",
    "C3_forcedP16_p10_c0_o0": "077953c31087c7577c86e77e1ddb42d9a07dad22562e5e31a141b25c4ba01e5d",
    "C3_forcedP16_p11_c0_o0": "c12a0e9c5ca7bb585e23705f314c6ce7c5519696a3c36abd7f70f10f511bf5e6",
    "C3_forcedP16_p12_c0_o0": "327792afa979ad3006fda482ac4985d7e1b53cc72a7f4bd4cd84a76f01e13569",
    "C3_forcedP16_p13_c0_o0": "c2aec3c845d4cea39a3bff521d06b76bc8ba119a1f18937b7bd41d68bccb5d34",
    "C3_forcedP16_p14_c0_o0": "7ba8bc4478d34fa917805d417ee0865076ed6208deb59d8804ae7599f98eb023",
    "C3_forcedP16_p15_c0_o0": "0599bb8e79c15b20282ad75dd1aaf960a10824c276edef53fe17a1aefdaa578c",
    "C3_forcedP16_p16_c0_o0": "0bc71fb1648dc2f3ff456e740da2b338f79b18882ac2c2ca3b5d420fe1551c2e",
    "C3_forcedP16_p17_c0_o0": "1071795cefe366620072299b27d3e0c6efcbdc3507753ebabb882232a7363ee9",
    "C3_forcedP16_p18_c0_o0": "ccfad86d52c077ecc27391b5282a408c5e9bacfc6b2ca60e0fe0dc5a464ec85c",
    "C3_forcedP16_p19_c0_o0": "339effb280ab52d0245382512be102ec6d5222caaa629df43ac494676c2a5d3a",
    "S10X_v7_s00_f01": "b8a60b47dfd72981da542dd425cca66c70331e39f944599fe420d2681ac53717",
    "S10X_forcedP16_s00_f01": "97f94a773ead82dc4b0c4b4327d79c1a1d4a6b499a1ce0a9fcb6fb230567fc50",
    "S10X_elite_s00_f01": "65d8fb58cb12a80d9031ad1b679c65ec4987abf2cc9c410b240171d87a8cb51c"
  },
  "subset": "First cluster 0/orientation 0 per drill/arm/opponent (56); first fight of series 0 per arm including full elite (3). Same allocated fights used by run.",
  "projection": {
    "remaining_projected_seconds": 4910.647185406565,
    "remaining_fights_max": 783,
    "workers": 6,
    "calibration_wall_seconds": 110.45479387500001,
    "measured_utilization": 0.899954903540246,
    "remaining_worker_seconds": 22096.805070313727,
    "safety_multiplier": 1.2,
    "series_chain_bound_seconds": 211.99095143312144,
    "categories": [
      {
        "group": "C1",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 86.63511484077807
      },
      {
        "group": "C1",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 84.67477400189976
      },
      {
        "group": "C2",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 44.93881809957747
      },
      {
        "group": "C2",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 72.422160202585
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "alone",
        "remaining": 9,
        "measured_full_horizon_seconds": 21.32224853678886
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "box",
        "remaining": 9,
        "measured_full_horizon_seconds": 22.655849662162137
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "column",
        "remaining": 9,
        "measured_full_horizon_seconds": 27.826096760991142
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "crescent",
        "remaining": 9,
        "measured_full_horizon_seconds": 28.937083085070704
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "line anvil",
        "remaining": 9,
        "measured_full_horizon_seconds": 31.50614566288722
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "line",
        "remaining": 9,
        "measured_full_horizon_seconds": 47.78935256568416
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "loose berserk",
        "remaining": 9,
        "measured_full_horizon_seconds": 32.699097898768265
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "loose free",
        "remaining": 9,
        "measured_full_horizon_seconds": 29.33839015192443
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "loose skirmish",
        "remaining": 9,
        "measured_full_horizon_seconds": 33.078199055198354
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "loose",
        "remaining": 9,
        "measured_full_horizon_seconds": 33.57704411162722
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "regular",
        "remaining": 9,
        "measured_full_horizon_seconds": 50.5816019286513
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "ring",
        "remaining": 9,
        "measured_full_horizon_seconds": 24.218167366614605
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "screen",
        "remaining": 9,
        "measured_full_horizon_seconds": 22.813118185459942
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "storm",
        "remaining": 9,
        "measured_full_horizon_seconds": 27.17176052061795
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "swarm",
        "remaining": 9,
        "measured_full_horizon_seconds": 29.91789852150479
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "wedge flank",
        "remaining": 9,
        "measured_full_horizon_seconds": 26.745743990383993
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "wedge hold",
        "remaining": 9,
        "measured_full_horizon_seconds": 26.156355577915384
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "wedge",
        "remaining": 9,
        "measured_full_horizon_seconds": 25.68108561220791
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "wide line",
        "remaining": 9,
        "measured_full_horizon_seconds": 33.96985903467089
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "wolfpack",
        "remaining": 9,
        "measured_full_horizon_seconds": 31.38214643978045
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "alone",
        "remaining": 9,
        "measured_full_horizon_seconds": 36.97419086534383
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "box",
        "remaining": 9,
        "measured_full_horizon_seconds": 49.516226693369475
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "column",
        "remaining": 9,
        "measured_full_horizon_seconds": 47.326912217409216
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "crescent",
        "remaining": 9,
        "measured_full_horizon_seconds": 45.078513936197474
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "line anvil",
        "remaining": 9,
        "measured_full_horizon_seconds": 41.32563273061627
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "line",
        "remaining": 9,
        "measured_full_horizon_seconds": 37.976108181818574
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "loose berserk",
        "remaining": 9,
        "measured_full_horizon_seconds": 20.89998808300001
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "loose free",
        "remaining": 9,
        "measured_full_horizon_seconds": 39.592996840569455
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "loose skirmish",
        "remaining": 9,
        "measured_full_horizon_seconds": 44.86324859161477
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "loose",
        "remaining": 9,
        "measured_full_horizon_seconds": 51.96363387096657
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "regular",
        "remaining": 9,
        "measured_full_horizon_seconds": 35.91738784090945
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "ring",
        "remaining": 9,
        "measured_full_horizon_seconds": 51.23642758140461
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "screen",
        "remaining": 9,
        "measured_full_horizon_seconds": 46.56517478479666
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "storm",
        "remaining": 9,
        "measured_full_horizon_seconds": 27.906433708592285
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "swarm",
        "remaining": 9,
        "measured_full_horizon_seconds": 36.24663596506273
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "wedge flank",
        "remaining": 9,
        "measured_full_horizon_seconds": 53.13949193166909
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "wedge hold",
        "remaining": 9,
        "measured_full_horizon_seconds": 54.34111142849561
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "wedge",
        "remaining": 9,
        "measured_full_horizon_seconds": 53.34558121508265
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "wide line",
        "remaining": 9,
        "measured_full_horizon_seconds": 34.780329333999994
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "wolfpack",
        "remaining": 9,
        "measured_full_horizon_seconds": 60.49442671589499
      },
      {
        "group": "D1",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 13.548459205977261
      },
      {
        "group": "D1",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 13.42656288109741
      },
      {
        "group": "D2",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 29.77623964490418
      },
      {
        "group": "D2",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 28.55405861333298
      },
      {
        "group": "D3",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 30.011273950000074
      },
      {
        "group": "D3",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 27.649742700000076
      },
      {
        "group": "D4",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 5.015905833000001
      },
      {
        "group": "D4",
        "arm": "v6",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 5.915157833
      },
      {
        "group": "D4",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 5.377013291
      },
      {
        "group": "D5",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 23.13738225
      },
      {
        "group": "D5",
        "arm": "v6",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 22.843135708000002
      },
      {
        "group": "D5",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 22.020768458
      },
      {
        "group": "S10X",
        "arm": "elite",
        "opponent": null,
        "remaining": 99,
        "measured_full_horizon_seconds": 21.199095143312142
      },
      {
        "group": "S10X",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 90,
        "measured_full_horizon_seconds": 11.242281389933355
      },
      {
        "group": "S10X",
        "arm": "v7",
        "opponent": null,
        "remaining": 90,
        "measured_full_horizon_seconds": 11.678343819354854
      }
    ],
    "method": "Per drill/arm/opponent and per series arm: sample wall seconds scaled to 150 simulated seconds (no downward scaling). Sum remaining work, divide by actual workers and measured utilization (completed sample work / calibration wall / workers, at most 1). Separate drill/series phases; series time at least the longest remaining sequential suffix. Apply 20% margin. Stopped series excluded.",
    "limits": "Fixed first cells are development timing samples, not a runtime guarantee. Later tactics, survivors and host load can differ. Only native execution, spooling and initial metrics are projected; standalone report/replay rendering is outside the compute cap."
  },
  "cap_seconds": 10800,
  "cap_file": "s4_shape_lab_v1/raw/LAB_CAP.json",
  "cap_file_sha256": "96064b88fdf42c0295fa6f1dbd9eff4f1796b95116dad3b35cce809425d38ea4",
  "approved_by": "owner",
  "date": "2026-10-08"
}
```

```json
{
  "status": "DONE",
  "seconds": 731.474819291,
  "cap_seconds": 10800,
  "cap_file": "s4_shape_lab_v1/raw/LAB_CAP.json",
  "cap_file_sha256": "96064b88fdf42c0295fa6f1dbd9eff4f1796b95116dad3b35cce809425d38ea4",
  "approved_by": "owner",
  "date": "2026-10-08",
  "declaration_sha256": "ab5bcf6eb0bb0ef4fef0c0575e38feb948d9ff1f4900317ac54aef21efc6bdd7",
  "calibration_sha256": "d76bfe61d901d32d102c24dce3b855f738d0a063f5c58b91ffb54b004675d38c",
  "projection": {
    "remaining_projected_seconds": 4910.647185406565,
    "remaining_fights_max": 783,
    "workers": 6,
    "calibration_wall_seconds": 110.45479387500001,
    "measured_utilization": 0.899954903540246,
    "remaining_worker_seconds": 22096.805070313727,
    "safety_multiplier": 1.2,
    "series_chain_bound_seconds": 211.99095143312144,
    "categories": [
      {
        "group": "C1",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 86.63511484077807
      },
      {
        "group": "C1",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 84.67477400189976
      },
      {
        "group": "C2",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 44.93881809957747
      },
      {
        "group": "C2",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 72.422160202585
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "alone",
        "remaining": 9,
        "measured_full_horizon_seconds": 21.32224853678886
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "box",
        "remaining": 9,
        "measured_full_horizon_seconds": 22.655849662162137
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "column",
        "remaining": 9,
        "measured_full_horizon_seconds": 27.826096760991142
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "crescent",
        "remaining": 9,
        "measured_full_horizon_seconds": 28.937083085070704
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "line anvil",
        "remaining": 9,
        "measured_full_horizon_seconds": 31.50614566288722
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "line",
        "remaining": 9,
        "measured_full_horizon_seconds": 47.78935256568416
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "loose berserk",
        "remaining": 9,
        "measured_full_horizon_seconds": 32.699097898768265
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "loose free",
        "remaining": 9,
        "measured_full_horizon_seconds": 29.33839015192443
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "loose skirmish",
        "remaining": 9,
        "measured_full_horizon_seconds": 33.078199055198354
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "loose",
        "remaining": 9,
        "measured_full_horizon_seconds": 33.57704411162722
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "regular",
        "remaining": 9,
        "measured_full_horizon_seconds": 50.5816019286513
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "ring",
        "remaining": 9,
        "measured_full_horizon_seconds": 24.218167366614605
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "screen",
        "remaining": 9,
        "measured_full_horizon_seconds": 22.813118185459942
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "storm",
        "remaining": 9,
        "measured_full_horizon_seconds": 27.17176052061795
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "swarm",
        "remaining": 9,
        "measured_full_horizon_seconds": 29.91789852150479
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "wedge flank",
        "remaining": 9,
        "measured_full_horizon_seconds": 26.745743990383993
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "wedge hold",
        "remaining": 9,
        "measured_full_horizon_seconds": 26.156355577915384
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "wedge",
        "remaining": 9,
        "measured_full_horizon_seconds": 25.68108561220791
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "wide line",
        "remaining": 9,
        "measured_full_horizon_seconds": 33.96985903467089
      },
      {
        "group": "C3",
        "arm": "forcedP16",
        "opponent": "wolfpack",
        "remaining": 9,
        "measured_full_horizon_seconds": 31.38214643978045
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "alone",
        "remaining": 9,
        "measured_full_horizon_seconds": 36.97419086534383
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "box",
        "remaining": 9,
        "measured_full_horizon_seconds": 49.516226693369475
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "column",
        "remaining": 9,
        "measured_full_horizon_seconds": 47.326912217409216
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "crescent",
        "remaining": 9,
        "measured_full_horizon_seconds": 45.078513936197474
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "line anvil",
        "remaining": 9,
        "measured_full_horizon_seconds": 41.32563273061627
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "line",
        "remaining": 9,
        "measured_full_horizon_seconds": 37.976108181818574
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "loose berserk",
        "remaining": 9,
        "measured_full_horizon_seconds": 20.89998808300001
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "loose free",
        "remaining": 9,
        "measured_full_horizon_seconds": 39.592996840569455
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "loose skirmish",
        "remaining": 9,
        "measured_full_horizon_seconds": 44.86324859161477
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "loose",
        "remaining": 9,
        "measured_full_horizon_seconds": 51.96363387096657
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "regular",
        "remaining": 9,
        "measured_full_horizon_seconds": 35.91738784090945
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "ring",
        "remaining": 9,
        "measured_full_horizon_seconds": 51.23642758140461
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "screen",
        "remaining": 9,
        "measured_full_horizon_seconds": 46.56517478479666
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "storm",
        "remaining": 9,
        "measured_full_horizon_seconds": 27.906433708592285
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "swarm",
        "remaining": 9,
        "measured_full_horizon_seconds": 36.24663596506273
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "wedge flank",
        "remaining": 9,
        "measured_full_horizon_seconds": 53.13949193166909
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "wedge hold",
        "remaining": 9,
        "measured_full_horizon_seconds": 54.34111142849561
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "wedge",
        "remaining": 9,
        "measured_full_horizon_seconds": 53.34558121508265
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "wide line",
        "remaining": 9,
        "measured_full_horizon_seconds": 34.780329333999994
      },
      {
        "group": "C3",
        "arm": "v7",
        "opponent": "wolfpack",
        "remaining": 9,
        "measured_full_horizon_seconds": 60.49442671589499
      },
      {
        "group": "D1",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 13.548459205977261
      },
      {
        "group": "D1",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 13.42656288109741
      },
      {
        "group": "D2",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 29.77623964490418
      },
      {
        "group": "D2",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 28.55405861333298
      },
      {
        "group": "D3",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 30.011273950000074
      },
      {
        "group": "D3",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 27.649742700000076
      },
      {
        "group": "D4",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 5.015905833000001
      },
      {
        "group": "D4",
        "arm": "v6",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 5.915157833
      },
      {
        "group": "D4",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 5.377013291
      },
      {
        "group": "D5",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 23.13738225
      },
      {
        "group": "D5",
        "arm": "v6",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 22.843135708000002
      },
      {
        "group": "D5",
        "arm": "v7",
        "opponent": null,
        "remaining": 9,
        "measured_full_horizon_seconds": 22.020768458
      },
      {
        "group": "S10X",
        "arm": "elite",
        "opponent": null,
        "remaining": 99,
        "measured_full_horizon_seconds": 21.199095143312142
      },
      {
        "group": "S10X",
        "arm": "forcedP16",
        "opponent": null,
        "remaining": 90,
        "measured_full_horizon_seconds": 11.242281389933355
      },
      {
        "group": "S10X",
        "arm": "v7",
        "opponent": null,
        "remaining": 90,
        "measured_full_horizon_seconds": 11.678343819354854
      }
    ],
    "method": "Per drill/arm/opponent and per series arm: sample wall seconds scaled to 150 simulated seconds (no downward scaling). Sum remaining work, divide by actual workers and measured utilization (completed sample work / calibration wall / workers, at most 1). Separate drill/series phases; series time at least the longest remaining sequential suffix. Apply 20% margin. Stopped series excluded.",
    "limits": "Fixed first cells are development timing samples, not a runtime guarantee. Later tactics, survivors and host load can differ. Only native execution, spooling and initial metrics are projected; standalone report/replay rendering is outside the compute cap."
  }
}
```

Process gate: **CLEAR**. 

## Per-drill results

Criteria apply per fight; the table reports how many fights met the complete conjunction. Missing observations are **not met (not evaluated)**, not measured failures. Conditional times and shares show evaluated denominators in JSON.

### D1

all enemy guns dead; own guns lost ≤1; gun damage share while enemy guns alive ≥60%

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 10 / 10 | {"t_enemy_guns_wiped":{"mean":10.833333333333306,"evaluated":10,"total":10},"own_guns_lost":{"mean":2,"evaluated":10,"total":10},"gun_damage_on_enemy_guns_share_while_guns_alive":{"mean":0.7640354579991557,"evaluated":10,"total":10},"own_shells_no_hit":{"mean":11,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | specified dummy/regular | 10 / 10 | {"t_enemy_guns_wiped":{"mean":10.933333333333305,"evaluated":10,"total":10},"own_guns_lost":{"mean":2,"evaluated":10,"total":10},"gun_damage_on_enemy_guns_share_while_guns_alive":{"mean":0.7405891980360065,"evaluated":10,"total":10},"own_shells_no_hit":{"mean":10,"evaluated":10,"total":10}} | not met (0/10 evaluated) |

### D2

≤1.5 own units hit per landed enemy shell

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 10 / 10 | {"own_units_hit_per_enemy_shell":{"mean":3.0754424263347024,"evaluated":10,"total":10},"damage_taken_per_enemy_shell":{"mean":41.876460420330666,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | specified dummy/regular | 10 / 10 | {"own_units_hit_per_enemy_shell":{"mean":4.343580342417552,"evaluated":10,"total":10},"damage_taken_per_enemy_shell":{"mean":58.38078204706112,"evaluated":10,"total":10}} | not met (0/10 evaluated) |

### D3

0 enemy ranged/melee damage to own guns

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 10 / 10 | {"damage_to_own_guns_by_source":{},"escorts_lost":{"mean":0,"evaluated":10,"total":10},"enemy_ranged_killed":{"mean":15,"evaluated":10,"total":10}} | met (10/10 evaluated) |
| forcedP16 | specified dummy/regular | 10 / 10 | {"damage_to_own_guns_by_source":{},"escorts_lost":{"mean":0,"evaluated":10,"total":10},"enemy_ranged_killed":{"mean":15,"evaluated":10,"total":10}} | met (10/10 evaluated) |

### D4

exchange >1:1; majority of melee survive

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 10 / 10 | {"exchange_ratio":{"mean":3.9233333333333333,"evaluated":10,"total":10},"melee_survivors":{"mean":6.7,"evaluated":10,"total":10}} | not met (7/10 evaluated) |
| forcedP16 | specified dummy/regular | 10 / 10 | {"exchange_ratio":{"mean":3.9233333333333333,"evaluated":10,"total":10},"melee_survivors":{"mean":6.7,"evaluated":10,"total":10}} | not met (7/10 evaluated) |
| v6 | specified dummy/regular | 10 / 10 | {"exchange_ratio":{"mean":null,"evaluated":0,"total":10},"melee_survivors":{"mean":10,"evaluated":10,"total":10}} | not met (9/10 evaluated) |

### D5

no units out of weapon reach during fight

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 10 / 10 | {"firepower_retained":{"mean":0.07585295716750447,"evaluated":10,"total":10},"units_out_of_fight":{"mean":27.6,"evaluated":10,"total":10},"own_lost":{"mean":6,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | specified dummy/regular | 10 / 10 | {"firepower_retained":{"mean":0.07585295716750447,"evaluated":10,"total":10},"units_out_of_fight":{"mean":27.6,"evaluated":10,"total":10},"own_lost":{"mean":6,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v6 | specified dummy/regular | 10 / 10 | {"firepower_retained":{"mean":0.01534325705398058,"evaluated":10,"total":10},"units_out_of_fight":{"mean":30,"evaluated":10,"total":10},"own_lost":{"mean":0,"evaluated":10,"total":10}} | not met (0/10 evaluated) |

### C1

elimination before 150s; no own losses

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 10 / 10 | {"win":{"mean":1,"evaluated":10,"total":10},"t_elimination":{"mean":33.76666666666724,"evaluated":10,"total":10},"own_lost":{"mean":2.9,"evaluated":10,"total":10}} | not met (2/10 evaluated) |
| forcedP16 | specified dummy/regular | 10 / 10 | {"win":{"mean":1,"evaluated":10,"total":10},"t_elimination":{"mean":33.76666666666724,"evaluated":10,"total":10},"own_lost":{"mean":2.9,"evaluated":10,"total":10}} | not met (2/10 evaluated) |

### C2

elimination before 150s; whole-army draft ≤4 own losses

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | specified dummy/regular | 10 / 10 | {"win":{"mean":1,"evaluated":10,"total":10},"t_elimination":{"mean":31.146666666667308,"evaluated":10,"total":10},"own_lost":{"mean":25.4,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | specified dummy/regular | 10 / 10 | {"win":{"mean":1,"evaluated":10,"total":10},"t_elimination":{"mean":31.340000000000707,"evaluated":10,"total":10},"own_lost":{"mean":29.4,"evaluated":10,"total":10}} | not met (0/10 evaluated) |

### C3

elimination before 150s; whole-army draft ≤4 own losses

| Arm | Opponent | Completed / planned | Section-4 metrics (means) | Draft criteria |
|---|---|---:|---|---|
| v7 | regular | 10 / 10 | {"win":{"mean":0.5,"evaluated":10,"total":10},"t_elimination":{"mean":44.02666666666673,"evaluated":5,"total":10},"own_lost":{"mean":46.5,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | line | 10 / 10 | {"win":{"mean":0.5,"evaluated":10,"total":10},"t_elimination":{"mean":44.02666666666673,"evaluated":5,"total":10},"own_lost":{"mean":46.5,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | wide line | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":47.4,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | wedge | 10 / 10 | {"win":{"mean":1,"evaluated":10,"total":10},"t_elimination":{"mean":36.190000000000396,"evaluated":10,"total":10},"own_lost":{"mean":38.3,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | box | 10 / 10 | {"win":{"mean":1,"evaluated":10,"total":10},"t_elimination":{"mean":39.203333333333646,"evaluated":10,"total":10},"own_lost":{"mean":36.9,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | column | 10 / 10 | {"win":{"mean":0.9,"evaluated":10,"total":10},"t_elimination":{"mean":34.40000000000049,"evaluated":9,"total":10},"own_lost":{"mean":37.3,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | loose | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":47.4,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | screen | 10 / 10 | {"win":{"mean":0.5,"evaluated":10,"total":10},"t_elimination":{"mean":40.49333333333358,"evaluated":5,"total":10},"own_lost":{"mean":45.1,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | crescent | 10 / 10 | {"win":{"mean":0.7,"evaluated":10,"total":10},"t_elimination":{"mean":45.60476190476186,"evaluated":7,"total":10},"own_lost":{"mean":41.8,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | ring | 10 / 10 | {"win":{"mean":1,"evaluated":10,"total":10},"t_elimination":{"mean":42.65000000000014,"evaluated":10,"total":10},"own_lost":{"mean":36.5,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | wedge hold | 10 / 10 | {"win":{"mean":1,"evaluated":10,"total":10},"t_elimination":{"mean":32.720000000000645,"evaluated":10,"total":10},"own_lost":{"mean":35.6,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | line anvil | 10 / 10 | {"win":{"mean":0.3,"evaluated":10,"total":10},"t_elimination":{"mean":52.544444444444025,"evaluated":3,"total":10},"own_lost":{"mean":48.3,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | wedge flank | 10 / 10 | {"win":{"mean":0.3,"evaluated":10,"total":10},"t_elimination":{"mean":66.58888888888768,"evaluated":3,"total":10},"own_lost":{"mean":48.2,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | loose free | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":50,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | swarm | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":50,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | loose skirmish | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":50,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | loose berserk | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":44,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | storm | 10 / 10 | {"win":{"mean":0.3,"evaluated":10,"total":10},"t_elimination":{"mean":37.23333333333378,"evaluated":3,"total":10},"own_lost":{"mean":48.1,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | wolfpack | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":50,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| v7 | alone | 10 / 10 | {"win":{"mean":0.1,"evaluated":10,"total":10},"t_elimination":{"mean":41.966666666666846,"evaluated":1,"total":10},"own_lost":{"mean":48.8,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | regular | 10 / 10 | {"win":{"mean":0.6,"evaluated":10,"total":10},"t_elimination":{"mean":45.805555555555515,"evaluated":6,"total":10},"own_lost":{"mean":47.1,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | line | 10 / 10 | {"win":{"mean":0.6,"evaluated":10,"total":10},"t_elimination":{"mean":45.805555555555515,"evaluated":6,"total":10},"own_lost":{"mean":47.1,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | wide line | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":50,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | wedge | 10 / 10 | {"win":{"mean":1,"evaluated":10,"total":10},"t_elimination":{"mean":38.130000000000386,"evaluated":10,"total":10},"own_lost":{"mean":41.5,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | box | 10 / 10 | {"win":{"mean":0.9,"evaluated":10,"total":10},"t_elimination":{"mean":37.50000000000042,"evaluated":9,"total":10},"own_lost":{"mean":41,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | column | 10 / 10 | {"win":{"mean":0.9,"evaluated":10,"total":10},"t_elimination":{"mean":33.414814814815365,"evaluated":9,"total":10},"own_lost":{"mean":41.6,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | loose | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":50,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | screen | 10 / 10 | {"win":{"mean":0.5,"evaluated":10,"total":10},"t_elimination":{"mean":44.933333333333344,"evaluated":5,"total":10},"own_lost":{"mean":47.9,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | crescent | 10 / 10 | {"win":{"mean":0.7,"evaluated":10,"total":10},"t_elimination":{"mean":40.585714285714545,"evaluated":7,"total":10},"own_lost":{"mean":45.2,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | ring | 10 / 10 | {"win":{"mean":1,"evaluated":10,"total":10},"t_elimination":{"mean":43.410000000000096,"evaluated":10,"total":10},"own_lost":{"mean":39.7,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | wedge hold | 10 / 10 | {"win":{"mean":1,"evaluated":10,"total":10},"t_elimination":{"mean":33.05666666666731,"evaluated":10,"total":10},"own_lost":{"mean":40.6,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | line anvil | 10 / 10 | {"win":{"mean":0.4,"evaluated":10,"total":10},"t_elimination":{"mean":55.46666666666608,"evaluated":4,"total":10},"own_lost":{"mean":48.4,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | wedge flank | 10 / 10 | {"win":{"mean":0.4,"evaluated":10,"total":10},"t_elimination":{"mean":59.508333333332516,"evaluated":4,"total":10},"own_lost":{"mean":48.4,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | loose free | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":50,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | swarm | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":50,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | loose skirmish | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":50,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | loose berserk | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":50,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | storm | 10 / 10 | {"win":{"mean":0.3,"evaluated":10,"total":10},"t_elimination":{"mean":44.2444444444445,"evaluated":3,"total":10},"own_lost":{"mean":48.7,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | wolfpack | 10 / 10 | {"win":{"mean":0,"evaluated":10,"total":10},"t_elimination":{"mean":null,"evaluated":0,"total":10},"own_lost":{"mean":50,"evaluated":10,"total":10}} | not met (0/10 evaluated) |
| forcedP16 | alone | 10 / 10 | {"win":{"mean":0.1,"evaluated":10,"total":10},"t_elimination":{"mean":48.09999999999983,"evaluated":1,"total":10},"own_lost":{"mean":49.5,"evaluated":10,"total":10}} | not met (0/10 evaluated) |

## S10X: abilities off; regular skills, uniform POOL replacement draws

| Arm | Series completed / 10 | Streak mean / median / min / max | Fight reached | Mean own losses per fight | Draft ≤4 losses |
|---|---:|---|---|---|---|
| v7 | 10 / 10 | {"mean": 0.4, "median": 0.0, "min": 0, "max": 1} | [1, 2, 2, 2, 1, 1, 1, 2, 1, 1] | 35.42857142857143 | not met |
| forcedP16 | 10 / 10 | {"mean": 0.2, "median": 0.0, "min": 0, "max": 1} | [1, 1, 2, 2, 1, 1, 1, 1, 1, 1] | 41.666666666666664 | not met |
| elite | 10 / 10 | {"mean": 2.7, "median": 2.0, "min": 1, "max": 5} | [3, 4, 6, 6, 2, 3, 3, 3, 3, 4] | 10.378378378378379 | not met |

Reference band: owner recollection of typical streak 6, sometimes 8; no statistical population claim.

### Units before each fight and per-tactic losses

| Arm | Series | Streak | Fight reached | Units before each fight |
|---|---:|---:|---:|---|
| v7 | 0 | 0 | 1 | [50] |
| v7 | 1 | 1 | 2 | [50, 9] |
| v7 | 2 | 1 | 2 | [50, 13] |
| v7 | 3 | 1 | 2 | [50, 13] |
| v7 | 4 | 0 | 1 | [50] |
| v7 | 5 | 0 | 1 | [50] |
| v7 | 6 | 0 | 1 | [50] |
| v7 | 7 | 1 | 2 | [50, 16] |
| v7 | 8 | 0 | 1 | [50] |
| v7 | 9 | 0 | 1 | [50] |
| forcedP16 | 0 | 0 | 1 | [50] |
| forcedP16 | 1 | 0 | 1 | [50] |
| forcedP16 | 2 | 1 | 2 | [50, 3] |
| forcedP16 | 3 | 1 | 2 | [50, 7] |
| forcedP16 | 4 | 0 | 1 | [50] |
| forcedP16 | 5 | 0 | 1 | [50] |
| forcedP16 | 6 | 0 | 1 | [50] |
| forcedP16 | 7 | 0 | 1 | [50] |
| forcedP16 | 8 | 0 | 1 | [50] |
| forcedP16 | 9 | 0 | 1 | [50] |
| elite | 0 | 2 | 3 | [50, 41, 37] |
| elite | 1 | 3 | 4 | [50, 42, 28, 17] |
| elite | 2 | 5 | 6 | [50, 48, 38, 33, 28, 13] |
| elite | 3 | 5 | 6 | [50, 47, 40, 39, 39, 15] |
| elite | 4 | 1 | 2 | [50, 42] |
| elite | 5 | 2 | 3 | [50, 47, 24] |
| elite | 6 | 2 | 3 | [50, 41, 15] |
| elite | 7 | 2 | 3 | [50, 41, 12] |
| elite | 8 | 2 | 3 | [50, 34, 27] |
| elite | 9 | 3 | 4 | [50, 27, 16, 8] |

| Arm | Tactic | Fights | Non-wins | Units lost total / mean |
|---|---|---:|---:|---|
| v7 | storm | 3 | 1 | 125 / 41.667 |
| v7 | wolfpack | 3 | 3 | 72 / 24.000 |
| v7 | wedge | 1 | 0 | 37 / 37.000 |
| v7 | crescent | 1 | 0 | 37 / 37.000 |
| v7 | loose berserk | 1 | 1 | 13 / 13.000 |
| v7 | loose skirmish | 2 | 2 | 100 / 50.000 |
| v7 | screen | 1 | 1 | 46 / 46.000 |
| v7 | wide line | 1 | 1 | 16 / 16.000 |
| v7 | loose free | 1 | 1 | 50 / 50.000 |
| forcedP16 | storm | 3 | 3 | 150 / 50.000 |
| forcedP16 | wedge | 1 | 0 | 47 / 47.000 |
| forcedP16 | wolfpack | 2 | 2 | 53 / 26.500 |
| forcedP16 | crescent | 1 | 0 | 43 / 43.000 |
| forcedP16 | loose berserk | 1 | 1 | 7 / 7.000 |
| forcedP16 | loose skirmish | 2 | 2 | 100 / 50.000 |
| forcedP16 | screen | 1 | 1 | 50 / 50.000 |
| forcedP16 | loose free | 1 | 1 | 50 / 50.000 |
| elite | storm | 5 | 1 | 49 / 9.800 |
| elite | crescent | 2 | 0 | 7 / 3.500 |
| elite | wide line | 3 | 1 | 65 / 21.667 |
| elite | wolfpack | 4 | 1 | 48 / 12.000 |
| elite | box | 3 | 1 | 24 / 8.000 |
| elite | wedge | 1 | 0 | 2 / 2.000 |
| elite | ring | 2 | 0 | 6 / 3.000 |
| elite | column | 1 | 0 | 5 / 5.000 |
| elite | loose free | 3 | 2 | 32 / 10.667 |
| elite | loose berserk | 3 | 2 | 41 / 13.667 |
| elite | wedge hold | 2 | 1 | 12 / 6.000 |
| elite | line anvil | 1 | 0 | 24 / 24.000 |
| elite | swarm | 1 | 1 | 1 / 1.000 |
| elite | loose skirmish | 2 | 0 | 24 / 12.000 |
| elite | screen | 1 | 0 | 3 / 3.000 |
| elite | alone | 1 | 0 | 26 / 26.000 |
| elite | wedge flank | 2 | 0 | 15 / 7.500 |

## Limits and definitions

- Drills planned: 560 fights; series at most 300. v6 uses delivered attempt-2 θ_v6 in D4 and D5; v7/forcedP16 use θ* ordinal 161. Elite retains full catalog planning and rollout behavior.
- D1 line axial separation is 500 px; cross-line diagonal distances can exceed 600 px. D5 starts 250 px apart. These geometries are declared before drills.
- Lab heading is radians stored as native guard direction; this engine has no general unit-facing state. Army-facing remains the scripted pack direction.
- Static dummies disable reflex dodges and restore their fixed post after native collision separation; other units still receive native collision pushes.
- All enemy-shell multiplicities use landed shells including zero-hit shells; unresolved shells at termination are censored. Firepower uses native range/gap with no extra margin and integrates all alive-unit seconds.
- D1 gun damage share includes only enemy damage while any enemy gun lives; friendly damage is excluded. Null shares mean no qualifying damage. Conditional kill times do not impute a 150-second success.
- The unchanged scorecard can read these observer streams via its RAW constant. Its hardcoded 50/10 denominators and reach+50 differ from reduced drills; it is explicitly auxiliary.
- Replay files retain every executed drill/series fight; deterministic sampling reduces FPS to enforce 8,000,000-byte limit. Replay index lists actual FPS. No replay is fabricated for an unrun fight.
- Slow-field launches are excluded from damaging-shell denominators. Raw entropy, requests, native streams and claims stay in ignored raw/. Immutable completions verify request/code/raw identity; Complete fights are never repeated. Native cap interruptions preserve partial files in raw/interrupted/ and retry that incomplete fight on resume; an unclosed attempt or other incomplete cell requires investigation.
- Delivery: UNCOMMITTED. Delivery bookkeeping pending.
- Process gate: CLEAR. Executed cells are listed above. Execution requires a clear repository-scoped pgrep gate and the measured remaining projection within the current local cap. Each invocation is capped; standalone report rendering is outside that compute cap.

## Local artifact inventory

- `s4_shape_lab_v3/.gitignore`
- `s4_shape_lab_v3/AUXILIARY_SCORECARD.json`
- `s4_shape_lab_v3/BUILD.json`
- `s4_shape_lab_v3/C1_SUMMARY.json`
- `s4_shape_lab_v3/C1_replays.json`
- `s4_shape_lab_v3/C2_SUMMARY.json`
- `s4_shape_lab_v3/C2_replays.json`
- `s4_shape_lab_v3/C3_SUMMARY.json`
- `s4_shape_lab_v3/C3_replays.json`
- `s4_shape_lab_v3/CALIBRATE_ATTEMPT_301b2e96b6ffd20f.json`
- `s4_shape_lab_v3/CALIBRATION.json`
- `s4_shape_lab_v3/CHECKS.json`
- `s4_shape_lab_v3/D1_SUMMARY.json`
- `s4_shape_lab_v3/D1_replays.json`
- `s4_shape_lab_v3/D2_SUMMARY.json`
- `s4_shape_lab_v3/D2_replays.json`
- `s4_shape_lab_v3/D3_SUMMARY.json`
- `s4_shape_lab_v3/D3_replays.json`
- `s4_shape_lab_v3/D4_SUMMARY.json`
- `s4_shape_lab_v3/D4_replays.json`
- `s4_shape_lab_v3/D5_SUMMARY.json`
- `s4_shape_lab_v3/D5_replays.json`
- `s4_shape_lab_v3/DECLARATION.json`
- `s4_shape_lab_v3/DELIVERY_GATE.json`
- `s4_shape_lab_v3/GATE_DISPOSITION.md`
- `s4_shape_lab_v3/GATE_TESTS.json`
- `s4_shape_lab_v3/GATE_TESTS.stderr.log`
- `s4_shape_lab_v3/GATE_TESTS.stdout.log`
- `s4_shape_lab_v3/OWNER_RECHECK_GATE.md`
- `s4_shape_lab_v3/PREPARE.json`
- `s4_shape_lab_v3/PREPARE.stderr.log`
- `s4_shape_lab_v3/PREPARE.stdout.log`
- `s4_shape_lab_v3/PREPARE_VERIFICATION.json`
- `s4_shape_lab_v3/PROCESS_GATE.json`
- `s4_shape_lab_v3/README.md`
- `s4_shape_lab_v3/REPLAY_INDEX.json`
- `s4_shape_lab_v3/RUN.json`
- `s4_shape_lab_v3/RUN_ATTEMPT_a84193878e007e0e.json`
- `s4_shape_lab_v3/RUN_GATE.json`
- `s4_shape_lab_v3/S10X_SUMMARY.json`
- `s4_shape_lab_v3/S10X_elite_s00_replays.json`
- `s4_shape_lab_v3/S10X_elite_s01_replays.json`
- `s4_shape_lab_v3/S10X_elite_s02_replays.json`
- `s4_shape_lab_v3/S10X_elite_s03_replays.json`
- `s4_shape_lab_v3/S10X_elite_s04_replays.json`
- `s4_shape_lab_v3/S10X_elite_s05_replays.json`
- `s4_shape_lab_v3/S10X_elite_s06_replays.json`
- `s4_shape_lab_v3/S10X_elite_s07_replays.json`
- `s4_shape_lab_v3/S10X_elite_s08_replays.json`
- `s4_shape_lab_v3/S10X_elite_s09_replays.json`
- `s4_shape_lab_v3/S10X_forcedP16_s00_replays.json`
- `s4_shape_lab_v3/S10X_forcedP16_s01_replays.json`
- `s4_shape_lab_v3/S10X_forcedP16_s02_replays.json`
- `s4_shape_lab_v3/S10X_forcedP16_s03_replays.json`
- `s4_shape_lab_v3/S10X_forcedP16_s04_replays.json`
- `s4_shape_lab_v3/S10X_forcedP16_s05_replays.json`
- `s4_shape_lab_v3/S10X_forcedP16_s06_replays.json`
- `s4_shape_lab_v3/S10X_forcedP16_s07_replays.json`
- `s4_shape_lab_v3/S10X_forcedP16_s08_replays.json`
- `s4_shape_lab_v3/S10X_forcedP16_s09_replays.json`
- `s4_shape_lab_v3/S10X_v7_s00_replays.json`
- `s4_shape_lab_v3/S10X_v7_s01_replays.json`
- `s4_shape_lab_v3/S10X_v7_s02_replays.json`
- `s4_shape_lab_v3/S10X_v7_s03_replays.json`
- `s4_shape_lab_v3/S10X_v7_s04_replays.json`
- `s4_shape_lab_v3/S10X_v7_s05_replays.json`
- `s4_shape_lab_v3/S10X_v7_s06_replays.json`
- `s4_shape_lab_v3/S10X_v7_s07_replays.json`
- `s4_shape_lab_v3/S10X_v7_s08_replays.json`
- `s4_shape_lab_v3/S10X_v7_s09_replays.json`
- `s4_shape_lab_v3/SCOPE_CHECK.json`
- `s4_shape_lab_v3/lab.py`
- `s4_shape_lab_v3/metrics.py`
- `s4_shape_lab_v3/replays.py`
- `s4_shape_lab_v3/report.py`
- `s4_shape_lab_v3/test_lab.py`
- `s4_shape_lab_v3/SHAPE_LAB_REPORT.md`

The native binary remains in ignored `s4_shape_lab_v1/build/`; v3 raw ledgers, streams and interruption archives stay in ignored `s4_shape_lab_v3/raw/`. This inventory is not a Git commit-status assertion.

## Owner recheck

See OWNER_RECHECK_GATE.md and GATE_DISPOSITION.md in this folder (separate Codex reviewer, same family).
The recheck and disposition are also tracked in docs/PLAN_CURRENT.md, which is excluded from this delivery commit.
