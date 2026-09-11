
// Auto-generated XGBoost Model — do not edit by hand.
// Regenerate with: python3 train_xgboost.py
// Used for Real-Time Win Probability Prediction in JumpOne
// Features expected in array order:
// [0] jumpSuccessRate, [1] jumpsFailed, [2] totalFalls, [3] maxFallDistance, [4] distancePerJump, [5] totalJumpsAttempted, [6] velocity_magnitude, [7] pos_x, [8] pos_y

// @ts-nocheck -- machine-generated body from m2cgen

function score(input) {
    var var0;
    if (input[8] < 4694.0) {
        if (input[0] < 0.72727275) {
            if (input[2] < 20.0) {
                var0 = 0.00891036;
            } else {
                var0 = -0.19807693;
            }
        } else {
            if (input[2] < 14.0) {
                var0 = 0.17482603;
            } else {
                var0 = -0.19333333;
            }
        }
    } else {
        if (input[8] < 6163.333) {
            if (input[5] < 30.0) {
                var0 = 0.0063958513;
            } else {
                var0 = -0.16285715;
            }
        } else {
            if (input[4] < 591.0108) {
                var0 = -0.178487;
            } else {
                var0 = 0.07526882;
            }
        }
    }
    var var1;
    if (input[8] < 4728.333) {
        if (input[1] < 23.0) {
            if (input[0] < 0.71794873) {
                var1 = 0.031889427;
            } else {
                var1 = 0.16519888;
            }
        } else {
            if (input[4] < 369.85754) {
                var1 = 0.10596635;
            } else {
                var1 = -0.09719183;
            }
        }
    } else {
        if (input[8] < 6000.8887) {
            if (input[5] < 30.0) {
                var1 = 0.031308144;
            } else {
                var1 = -0.1472611;
            }
        } else {
            if (input[4] < 591.0108) {
                var1 = -0.15925236;
            } else {
                var1 = 0.06538066;
            }
        }
    }
    var var2;
    if (input[8] < 4438.0) {
        if (input[2] < 18.0) {
            if (input[0] < 0.6944444) {
                var2 = -0.015797343;
            } else {
                var2 = 0.14920408;
            }
        } else {
            if (input[0] < 0.65384614) {
                var2 = 0.14936648;
            } else {
                var2 = -0.17353629;
            }
        }
    } else {
        if (input[8] < 5582.889) {
            if (input[1] < 4.0) {
                var2 = 0.15836889;
            } else {
                var2 = -0.092685714;
            }
        } else {
            if (input[4] < 591.0108) {
                var2 = -0.13805963;
            } else {
                var2 = 0.059283115;
            }
        }
    }
    var var3;
    if (input[8] < 4438.0) {
        if (input[2] < 18.0) {
            if (input[0] < 0.6944444) {
                var3 = -0.01422468;
            } else {
                var3 = 0.13816662;
            }
        } else {
            if (input[0] < 0.65384614) {
                var3 = 0.13858756;
            } else {
                var3 = -0.16165195;
            }
        }
    } else {
        if (input[8] < 6000.8887) {
            if (input[1] < 4.0) {
                var3 = 0.102275625;
            } else {
                var3 = -0.10235237;
            }
        } else {
            if (input[4] < 591.0108) {
                var3 = -0.13634165;
            } else {
                var3 = 0.053838994;
            }
        }
    }
    var var4;
    if (input[8] < 4728.333) {
        if (input[1] < 23.0) {
            if (input[4] < 348.00616) {
                var4 = 0.014229441;
            } else {
                var4 = 0.13534299;
            }
        } else {
            if (input[4] < 369.85754) {
                var4 = 0.08503312;
            } else {
                var4 = -0.07996027;
            }
        }
    } else {
        if (input[8] < 6230.0) {
            if (input[5] < 30.0) {
                var4 = 0.009305391;
            } else {
                var4 = -0.121791616;
            }
        } else {
            if (input[4] < 591.0108) {
                var4 = -0.13096558;
            } else {
                var4 = 0.051127333;
            }
        }
    }
    var var5;
    if (input[8] < 5014.0) {
        if (input[1] < 34.0) {
            if (input[0] < 0.7222222) {
                var5 = -0.005010165;
            } else {
                var5 = 0.11911153;
            }
        } else {
            if (input[4] < 363.4855) {
                var5 = 0.12933803;
            } else {
                var5 = -0.08022832;
            }
        }
    } else {
        if (input[8] < 6322.3335) {
            if (input[5] < 30.0) {
                var5 = -0.02722851;
            } else {
                var5 = -0.12531249;
            }
        } else {
            if (input[4] < 591.0108) {
                var5 = -0.1273697;
            } else {
                var5 = 0.04051067;
            }
        }
    }
    var var6;
    if (input[8] < 4410.6665) {
        if (input[2] < 18.0) {
            if (input[0] < 0.6944444) {
                var6 = -0.009054723;
            } else {
                var6 = 0.11676399;
            }
        } else {
            if (input[0] < 0.65384614) {
                var6 = 0.14007622;
            } else {
                var6 = -0.14442793;
            }
        }
    } else {
        if (input[8] < 6000.8887) {
            if (input[5] < 33.0) {
                var6 = 0.04271119;
            } else {
                var6 = -0.10075823;
            }
        } else {
            if (input[2] < 13.0) {
                var6 = -0.112275235;
            } else {
                var6 = 0.27385038;
            }
        }
    }
    var var7;
    if (input[8] < 5014.0) {
        if (input[0] < 0.7818182) {
            if (input[4] < 391.03403) {
                var7 = 0.028555397;
            } else {
                var7 = -0.1239857;
            }
        } else {
            if (input[3] < 133.99983) {
                var7 = 0.04391608;
            } else {
                var7 = 0.12231908;
            }
        }
    } else {
        if (input[8] < 6322.3335) {
            if (input[1] < 4.0) {
                var7 = 0.006970051;
            } else {
                var7 = -0.096982636;
            }
        } else {
            if (input[4] < 591.0108) {
                var7 = -0.11522875;
            } else {
                var7 = 0.04692097;
            }
        }
    }
    var var8;
    if (input[8] < 4438.0) {
        if (input[2] < 18.0) {
            if (input[0] < 0.6944444) {
                var8 = -0.009093929;
            } else {
                var8 = 0.10676497;
            }
        } else {
            if (input[0] < 0.65384614) {
                var8 = 0.12903601;
            } else {
                var8 = -0.13679856;
            }
        }
    } else {
        if (input[8] < 5582.889) {
            if (input[1] < 4.0) {
                var8 = 0.12586181;
            } else {
                var8 = -0.0573797;
            }
        } else {
            if (input[5] < 11.0) {
                var8 = -0.068284295;
            } else {
                var8 = -0.11163824;
            }
        }
    }
    var var9;
    if (input[8] < 4410.6665) {
        if (input[2] < 18.0) {
            if (input[0] < 0.6944444) {
                var9 = -0.0076914662;
            } else {
                var9 = 0.101257764;
            }
        } else {
            if (input[0] < 0.65384614) {
                var9 = 0.121419124;
            } else {
                var9 = -0.13188785;
            }
        }
    } else {
        if (input[8] < 6163.333) {
            if (input[5] < 34.0) {
                var9 = 0.025684452;
            } else {
                var9 = -0.08874199;
            }
        } else {
            if (input[0] < 0.51724136) {
                var9 = -0.046804316;
            } else {
                var9 = -0.11097268;
            }
        }
    }
    var var10;
    if (input[8] < 5014.0) {
        if (input[0] < 0.7818182) {
            if (input[4] < 391.03403) {
                var10 = 0.024707576;
            } else {
                var10 = -0.1138041;
            }
        } else {
            if (input[1] < 1.0) {
                var10 = -0.03735363;
            } else {
                var10 = 0.10664555;
            }
        }
    } else {
        if (input[3] < 518.0002) {
            if (input[3] < 326.00015) {
                var10 = -0.065636456;
            } else {
                var10 = -0.11985284;
            }
        } else {
            if (input[5] < 25.0) {
                var10 = 0.22903383;
            } else {
                var10 = -0.07795193;
            }
        }
    }
    var var11;
    if (input[8] < 5398.0) {
        if (input[0] < 0.7818182) {
            if (input[0] < 0.5903614) {
                var11 = 0.27227518;
            } else {
                var11 = -0.012315829;
            }
        } else {
            if (input[4] < 352.18765) {
                var11 = -0.0274506;
            } else {
                var11 = 0.1023394;
            }
        }
    } else {
        if (input[5] < 17.0) {
            if (input[3] < 518.0002) {
                var11 = -0.06913363;
            } else {
                var11 = 0.22807513;
            }
        } else {
            if (input[2] < 13.0) {
                var11 = -0.10846483;
            } else {
                var11 = 0.21201368;
            }
        }
    }
    var var12;
    if (input[8] < 3734.0) {
        if (input[0] < 0.7297297) {
            if (input[4] < 360.7221) {
                var12 = 0.09626157;
            } else {
                var12 = -0.03421854;
            }
        } else {
            if (input[2] < 14.0) {
                var12 = 0.108097136;
            } else {
                var12 = -0.124051705;
            }
        }
    } else {
        if (input[3] < 518.0002) {
            if (input[3] < 326.00015) {
                var12 = -0.04659958;
            } else {
                var12 = -0.116414905;
            }
        } else {
            if (input[1] < 8.0) {
                var12 = 0.14468448;
            } else {
                var12 = -0.053354997;
            }
        }
    }
    var var13;
    if (input[8] < 3734.0) {
        if (input[2] < 18.0) {
            if (input[0] < 0.6944444) {
                var13 = -0.008403918;
            } else {
                var13 = 0.10362575;
            }
        } else {
            if (input[0] < 0.65384614) {
                var13 = 0.1159758;
            } else {
                var13 = -0.12511991;
            }
        }
    } else {
        if (input[8] < 6322.3335) {
            if (input[1] < 4.0) {
                var13 = 0.044724017;
            } else {
                var13 = -0.052010354;
            }
        } else {
            if (input[4] < 591.0108) {
                var13 = -0.09265904;
            } else {
                var13 = 0.07520606;
            }
        }
    }
    var var14;
    if (input[8] < 5398.0) {
        if (input[2] < 18.0) {
            if (input[0] < 0.5903614) {
                var14 = 0.24566734;
            } else {
                var14 = 0.027904127;
            }
        } else {
            if (input[0] < 0.65384614) {
                var14 = 0.11006384;
            } else {
                var14 = -0.12376702;
            }
        }
    } else {
        if (input[5] < 18.0) {
            if (input[3] < 518.0002) {
                var14 = -0.058628287;
            } else {
                var14 = 0.19378607;
            }
        } else {
            if (input[2] < 13.0) {
                var14 = -0.099912874;
            } else {
                var14 = 0.19510974;
            }
        }
    }
    var var15;
    if (input[8] < 3734.0) {
        if (input[0] < 0.7297297) {
            if (input[4] < 359.12286) {
                var15 = 0.100089215;
            } else {
                var15 = -0.028661598;
            }
        } else {
            if (input[2] < 14.0) {
                var15 = 0.099971525;
            } else {
                var15 = -0.11881416;
            }
        }
    } else {
        if (input[3] < 518.0002) {
            if (input[3] < 326.00015) {
                var15 = -0.035918772;
            } else {
                var15 = -0.108438365;
            }
        } else {
            if (input[1] < 8.0) {
                var15 = 0.13354532;
            } else {
                var15 = -0.044647183;
            }
        }
    }
    var var16;
    if (input[8] < 5014.0) {
        if (input[1] < 23.0) {
            if (input[4] < 348.00616) {
                var16 = -0.04456548;
            } else {
                var16 = 0.08309697;
            }
        } else {
            if (input[3] < 1094.0) {
                var16 = -0.10631253;
            } else {
                var16 = 0.025249556;
            }
        }
    } else {
        if (input[8] < 6358.0) {
            if (input[5] < 30.0) {
                var16 = 0.007763769;
            } else {
                var16 = -0.080299936;
            }
        } else {
            if (input[4] < 302.21844) {
                var16 = -0.010903562;
            } else {
                var16 = -0.09346971;
            }
        }
    }
    var var17;
    if (input[8] < 5582.889) {
        if (input[2] < 18.0) {
            if (input[0] < 0.5903614) {
                var17 = 0.20967694;
            } else {
                var17 = 0.021320742;
            }
        } else {
            if (input[0] < 0.65384614) {
                var17 = 0.10498943;
            } else {
                var17 = -0.12029374;
            }
        }
    } else {
        if (input[5] < 10.0) {
            if (input[8] < 6230.0) {
                var17 = 0.073345356;
            } else {
                var17 = -0.051864296;
            }
        } else {
            if (input[2] < 13.0) {
                var17 = -0.08455103;
            } else {
                var17 = 0.19176202;
            }
        }
    }
    var var18;
    if (input[3] < 518.0002) {
        if (input[3] < 326.00015) {
            if (input[3] < 262.00006) {
                var18 = -0.039744794;
            } else {
                var18 = 0.1251856;
            }
        } else {
            if (input[8] < 3286.0) {
                var18 = 0.07784055;
            } else {
                var18 = -0.10468743;
            }
        }
    } else {
        if (input[3] < 646.0002) {
            if (input[4] < 351.8594) {
                var18 = -0.037374854;
            } else {
                var18 = 0.13602506;
            }
        } else {
            if (input[4] < 369.85754) {
                var18 = 0.06984194;
            } else {
                var18 = -0.0427755;
            }
        }
    }
    var var19;
    if (input[8] < 3670.0) {
        if (input[0] < 0.71794873) {
            if (input[0] < 0.65384614) {
                var19 = 0.10059982;
            } else {
                var19 = -0.04723649;
            }
        } else {
            if (input[2] < 14.0) {
                var19 = 0.09844023;
            } else {
                var19 = -0.105783544;
            }
        }
    } else {
        if (input[8] < 6358.0) {
            if (input[1] < 4.0) {
                var19 = 0.044450443;
            } else {
                var19 = -0.037488654;
            }
        } else {
            if (input[4] < 302.2184) {
                var19 = 0.005950797;
            } else {
                var19 = -0.08454005;
            }
        }
    }
    var var20;
    if (input[3] < 518.0002) {
        if (input[3] < 326.00015) {
            if (input[3] < 262.00006) {
                var20 = -0.035129923;
            } else {
                var20 = 0.1157506;
            }
        } else {
            if (input[8] < 3286.0) {
                var20 = 0.07135755;
            } else {
                var20 = -0.09970667;
            }
        }
    } else {
        if (input[3] < 646.0002) {
            if (input[4] < 351.8594) {
                var20 = -0.03165019;
            } else {
                var20 = 0.13067816;
            }
        } else {
            if (input[4] < 367.89493) {
                var20 = 0.071389355;
            } else {
                var20 = -0.03587606;
            }
        }
    }
    var var21;
    if (input[3] < 518.0002) {
        if (input[3] < 326.00015) {
            if (input[3] < 262.00006) {
                var21 = -0.032156117;
            } else {
                var21 = 0.10583811;
            }
        } else {
            if (input[8] < 3286.0) {
                var21 = 0.06810207;
            } else {
                var21 = -0.09601381;
            }
        }
    } else {
        if (input[3] < 646.0002) {
            if (input[4] < 351.8594) {
                var21 = -0.028934894;
            } else {
                var21 = 0.12361189;
            }
        } else {
            if (input[4] < 367.39026) {
                var21 = 0.067925476;
            } else {
                var21 = -0.031884916;
            }
        }
    }
    var var22;
    if (input[8] < 6000.8887) {
        if (input[0] < 0.5903614) {
            if (input[8] < 5215.3887) {
                var22 = 0.22376065;
            } else {
                var22 = 0.035406664;
            }
        } else {
            if (input[0] < 0.7818182) {
                var22 = -0.016033456;
            } else {
                var22 = 0.054297484;
            }
        }
    } else {
        if (input[0] < 0.51724136) {
            if (input[7] < 698.5) {
                var22 = 0.0019410662;
            } else {
                var22 = 0.37025842;
            }
        } else {
            if (input[2] < 13.0) {
                var22 = -0.07451026;
            } else {
                var22 = 0.2175041;
            }
        }
    }
    var var23;
    if (input[8] < 3926.0) {
        if (input[0] < 0.7297297) {
            if (input[3] < 1094.0) {
                var23 = -0.13933918;
            } else {
                var23 = 0.0143986065;
            }
        } else {
            if (input[2] < 14.0) {
                var23 = 0.086808115;
            } else {
                var23 = -0.10773033;
            }
        }
    } else {
        if (input[0] < 0.6111111) {
            if (input[8] < 5499.3335) {
                var23 = 0.15564679;
            } else {
                var23 = -0.005543167;
            }
        } else {
            if (input[8] < 6265.6665) {
                var23 = -0.028915739;
            } else {
                var23 = -0.08767175;
            }
        }
    }
    var var24;
    if (input[3] < 1094.0) {
        if (input[3] < 1022.33374) {
            if (input[3] < 518.0002) {
                var24 = -0.038305145;
            } else {
                var24 = 0.04498887;
            }
        } else {
            if (input[0] < 0.7818182) {
                var24 = -0.14258762;
            } else {
                var24 = -0.7155351;
            }
        }
    } else {
        if (input[3] < 1414.0) {
            if (input[0] < 0.6960784) {
                var24 = 0.021159356;
            } else {
                var24 = 0.12487077;
            }
        } else {
            if (input[4] < 363.4855) {
                var24 = 0.13462017;
            } else {
                var24 = -0.13429935;
            }
        }
    }
    var var25;
    if (input[8] < 6046.6665) {
        if (input[1] < 4.0) {
            if (input[4] < 550.24756) {
                var25 = 0.087621845;
            } else {
                var25 = -0.06915453;
            }
        } else {
            if (input[3] < 518.0002) {
                var25 = -0.07983397;
            } else {
                var25 = 0.012812159;
            }
        }
    } else {
        if (input[0] < 0.51724136) {
            if (input[7] < 698.5) {
                var25 = 0.006519982;
            } else {
                var25 = 0.2967508;
            }
        } else {
            if (input[4] < 591.0108) {
                var25 = -0.0768843;
            } else {
                var25 = 0.10629811;
            }
        }
    }
    var var26;
    if (input[8] < 3926.0) {
        if (input[0] < 0.7297297) {
            if (input[0] < 0.6388889) {
                var26 = 0.10372584;
            } else {
                var26 = -0.036760077;
            }
        } else {
            if (input[4] < 385.53183) {
                var26 = 0.09041107;
            } else {
                var26 = -0.0029208958;
            }
        }
    } else {
        if (input[0] < 0.6111111) {
            if (input[8] < 5499.3335) {
                var26 = 0.13180116;
            } else {
                var26 = -0.0003988918;
            }
        } else {
            if (input[1] < 9.0) {
                var26 = -0.014772638;
            } else {
                var26 = -0.0710092;
            }
        }
    }
    var var27;
    if (input[3] < 1094.0) {
        if (input[3] < 1022.33374) {
            if (input[3] < 518.0002) {
                var27 = -0.03255413;
            } else {
                var27 = 0.040467072;
            }
        } else {
            if (input[0] < 0.7818182) {
                var27 = -0.13769229;
            } else {
                var27 = -0.4586475;
            }
        }
    } else {
        if (input[3] < 1414.0) {
            if (input[0] < 0.6960784) {
                var27 = 0.017835524;
            } else {
                var27 = 0.12307316;
            }
        } else {
            if (input[4] < 363.4855) {
                var27 = 0.12886433;
            } else {
                var27 = -0.12780927;
            }
        }
    }
    var var28;
    if (input[8] < 6443.3335) {
        if (input[2] < 20.0) {
            if (input[1] < 117.0) {
                var28 = 0.003166442;
            } else {
                var28 = 0.15082936;
            }
        } else {
            var28 = -0.11177971;
        }
    } else {
        if (input[4] < 302.21844) {
            if (input[1] < 2.0) {
                var28 = -0.009242925;
            } else {
                var28 = 0.37754524;
            }
        } else {
            if (input[4] < 550.24756) {
                var28 = -0.09191608;
            } else {
                var28 = 0.17234574;
            }
        }
    }
    var var29;
    if (input[8] < 6358.0) {
        if (input[0] < 0.6111111) {
            if (input[4] < 442.09158) {
                var29 = 0.10919058;
            } else {
                var29 = -0.02589925;
            }
        } else {
            if (input[0] < 0.7906977) {
                var29 = -0.019218367;
            } else {
                var29 = 0.042361416;
            }
        }
    } else {
        if (input[4] < 591.0108) {
            if (input[4] < 302.21844) {
                var29 = 0.014779349;
            } else {
                var29 = -0.07949145;
            }
        } else {
            if (input[4] < 723.3236) {
                var29 = 0.2007699;
            } else {
                var29 = -0.02854349;
            }
        }
    }
    var var30;
    var30 = sigmoid(var0 + var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 + var20 + var21 + var22 + var23 + var24 + var25 + var26 + var27 + var28 + var29);
    return [1.0 - var30, var30];
}
function sigmoid(x) {
    if (x < 0.0) {
        var z = Math.exp(x);
        return z / (1.0 + z);
    }
    return 1.0 / (1.0 + Math.exp(-x));
}


// m2cgen emits 'function score(input) { ... }'.
// For a binary classifier it already applies the sigmoid internally and
// returns [P(class 0), P(class 1)] — do NOT apply a sigmoid again.
export function predictWinProbability(features: number[]): number {
    const out = score(features);
    return Array.isArray(out)
        ? out[out.length - 1]        // classifier: last entry is P(win)
        : 1 / (1 + Math.exp(-out));  // regressor: raw logit
}
