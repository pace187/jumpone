
// Auto-generated XGBoost Model — do not edit by hand.
// Regenerate with: python3 train_xgboost.py
// Used for Real-Time Win Probability Prediction in JumpOne
// Features expected in array order:
// [0] jumpSuccessRate, [1] jumpsFailed, [2] totalFalls, [3] maxFallDistance, [4] distancePerJump, [5] totalJumpsAttempted, [6] velocity_magnitude, [7] pos_x, [8] pos_y

// @ts-nocheck -- machine-generated body from m2cgen

function score(input) {
    var var0;
    if (input[8] < 4940.0) {
        if (input[4] < 391.02856) {
            if (input[0] < 0.7075472) {
                var0 = 0.03511954;
            } else {
                var0 = 0.16186808;
            }
        } else {
            if (input[0] < 0.64444447) {
                var0 = 0.13793103;
            } else {
                var0 = -0.17831326;
            }
        }
    } else {
        if (input[1] < 44.0) {
            if (input[8] < 6159.7227) {
                var0 = -0.124658346;
            } else {
                var0 = -0.17735618;
            }
        } else {
            if (input[1] < 73.0) {
                var0 = 0.18297873;
            } else {
                var0 = 0.05;
            }
        }
    }
    var var1;
    if (input[8] < 4694.0) {
        if (input[4] < 391.02856) {
            if (input[0] < 0.6944444) {
                var1 = 0.023421101;
            } else {
                var1 = 0.15277794;
            }
        } else {
            if (input[0] < 0.64) {
                var1 = 0.1482384;
            } else {
                var1 = -0.16363923;
            }
        }
    } else {
        if (input[3] < 1094.0) {
            if (input[8] < 5570.3335) {
                var1 = -0.07819941;
            } else {
                var1 = -0.15418337;
            }
        } else {
            if (input[4] < 387.51608) {
                var1 = 0.18477952;
            } else {
                var1 = -0.061853655;
            }
        }
    }
    var var2;
    if (input[8] < 4694.0) {
        if (input[4] < 391.02856) {
            if (input[0] < 0.6944444) {
                var2 = 0.021100176;
            } else {
                var2 = 0.14007755;
            }
        } else {
            if (input[3] < 646.00024) {
                var2 = 0.17379738;
            } else {
                var2 = -0.14888181;
            }
        }
    } else {
        if (input[3] < 1094.0) {
            if (input[8] < 6010.0) {
                var2 = -0.08958599;
            } else {
                var2 = -0.14773946;
            }
        } else {
            if (input[4] < 387.51608) {
                var2 = 0.16935366;
            } else {
                var2 = -0.058550764;
            }
        }
    }
    var var3;
    if (input[8] < 4694.0) {
        if (input[4] < 391.02856) {
            if (input[0] < 0.6972477) {
                var3 = 0.020626811;
            } else {
                var3 = 0.13052092;
            }
        } else {
            if (input[0] < 0.64) {
                var3 = 0.14518212;
            } else {
                var3 = -0.1415851;
            }
        }
    } else {
        if (input[3] < 1094.0) {
            if (input[8] < 5570.3335) {
                var3 = -0.062432446;
            } else {
                var3 = -0.13136901;
            }
        } else {
            if (input[4] < 387.51608) {
                var3 = 0.15732993;
            } else {
                var3 = -0.055479135;
            }
        }
    }
    var var4;
    if (input[8] < 5014.0) {
        if (input[4] < 391.02856) {
            if (input[0] < 0.7075472) {
                var4 = 0.01970013;
            } else {
                var4 = 0.11040439;
            }
        } else {
            if (input[3] < 837.9999) {
                var4 = 0.16869688;
            } else {
                var4 = -0.13451657;
            }
        }
    } else {
        if (input[1] < 44.0) {
            if (input[1] < 2.0) {
                var4 = -0.0828787;
            } else {
                var4 = -0.1298295;
            }
        } else {
            var4 = 0.16183716;
        }
    }
    var var5;
    if (input[8] < 4438.0) {
        if (input[4] < 391.02856) {
            if (input[0] < 0.6944444) {
                var5 = 0.01370419;
            } else {
                var5 = 0.122388415;
            }
        } else {
            if (input[0] < 0.65217394) {
                var5 = 0.10809207;
            } else {
                var5 = -0.13954996;
            }
        }
    } else {
        if (input[3] < 1094.0) {
            if (input[8] < 6010.0) {
                var5 = -0.06744567;
            } else {
                var5 = -0.12178;
            }
        } else {
            if (input[4] < 388.15225) {
                var5 = 0.15766923;
            } else {
                var5 = -0.101924434;
            }
        }
    }
    var var6;
    if (input[8] < 4407.5557) {
        if (input[4] < 391.02856) {
            if (input[0] < 0.7051282) {
                var6 = 0.01689615;
            } else {
                var6 = 0.119091466;
            }
        } else {
            if (input[0] < 0.65217394) {
                var6 = 0.10397668;
            } else {
                var6 = -0.13310492;
            }
        }
    } else {
        if (input[3] < 1094.0) {
            if (input[8] < 6010.0) {
                var6 = -0.061867774;
            } else {
                var6 = -0.11496289;
            }
        } else {
            if (input[4] < 388.15225) {
                var6 = 0.14920111;
            } else {
                var6 = -0.0950851;
            }
        }
    }
    var var7;
    if (input[8] < 4407.5557) {
        if (input[4] < 391.02856) {
            if (input[0] < 0.6944444) {
                var7 = 0.010193617;
            } else {
                var7 = 0.109891966;
            }
        } else {
            if (input[0] < 0.65217394) {
                var7 = 0.09514466;
            } else {
                var7 = -0.1276143;
            }
        }
    } else {
        if (input[3] < 1094.0) {
            if (input[1] < 3.0) {
                var7 = -0.05254668;
            } else {
                var7 = -0.10808771;
            }
        } else {
            if (input[4] < 388.15225) {
                var7 = 0.14100212;
            } else {
                var7 = -0.08894856;
            }
        }
    }
    var var8;
    if (input[8] < 5014.0) {
        if (input[2] < 2.0) {
            if (input[1] < 1.0) {
                var8 = -0.17888777;
            } else {
                var8 = 0.13764906;
            }
        } else {
            if (input[3] < 517.99994) {
                var8 = -0.20707801;
            } else {
                var8 = 0.030873476;
            }
        }
    } else {
        if (input[1] < 44.0) {
            if (input[1] < 2.0) {
                var8 = -0.055879235;
            } else {
                var8 = -0.10539444;
            }
        } else {
            var8 = 0.16033767;
        }
    }
    var var9;
    if (input[8] < 5014.0) {
        if (input[2] < 2.0) {
            if (input[1] < 1.0) {
                var9 = -0.16551435;
            } else {
                var9 = 0.13045253;
            }
        } else {
            if (input[0] < 0.64) {
                var9 = 0.16786705;
            } else {
                var9 = -0.0064426996;
            }
        }
    } else {
        if (input[8] < 6230.0) {
            if (input[1] < 2.0) {
                var9 = 0.23890792;
            } else {
                var9 = -0.07967158;
            }
        } else {
            if (input[4] < 302.21844) {
                var9 = -0.036978956;
            } else {
                var9 = -0.11403384;
            }
        }
    }
    var var10;
    if (input[8] < 4407.5557) {
        if (input[4] < 369.85754) {
            if (input[3] < 1221.9999) {
                var10 = 0.051763207;
            } else {
                var10 = 0.12983988;
            }
        } else {
            if (input[0] < 0.64444447) {
                var10 = 0.15551424;
            } else {
                var10 = -0.07824308;
            }
        }
    } else {
        if (input[8] < 6230.0) {
            if (input[1] < 4.0) {
                var10 = 0.14330332;
            } else {
                var10 = -0.074899964;
            }
        } else {
            if (input[4] < 302.21844) {
                var10 = -0.03395583;
            } else {
                var10 = -0.10941485;
            }
        }
    }
    var var11;
    if (input[8] < 5398.0) {
        if (input[0] < 0.6296296) {
            if (input[8] < 4806.0) {
                var11 = 0.15655117;
            } else {
                var11 = 0.24581657;
            }
        } else {
            if (input[4] < 377.2652) {
                var11 = 0.046265807;
            } else {
                var11 = -0.07297655;
            }
        }
    } else {
        if (input[0] < 0.5090909) {
            if (input[8] < 6359.0) {
                var11 = 0.15158577;
            } else {
                var11 = -0.0616283;
            }
        } else {
            if (input[4] < 430.2517) {
                var11 = -0.10730585;
            } else {
                var11 = -0.050703585;
            }
        }
    }
    var var12;
    if (input[8] < 4407.5557) {
        if (input[0] < 0.6972477) {
            if (input[0] < 0.64444447) {
                var12 = 0.14081351;
            } else {
                var12 = -0.06384011;
            }
        } else {
            if (input[4] < 385.46545) {
                var12 = 0.09943025;
            } else {
                var12 = -0.099161185;
            }
        }
    } else {
        if (input[8] < 6230.0) {
            if (input[1] < 4.0) {
                var12 = 0.13222735;
            } else {
                var12 = -0.06803075;
            }
        } else {
            if (input[4] < 302.21844) {
                var12 = -0.026108405;
            } else {
                var12 = -0.10214654;
            }
        }
    }
    var var13;
    if (input[8] < 5570.3335) {
        if (input[0] < 0.64) {
            if (input[4] < 374.32114) {
                var13 = -0.036047842;
            } else {
                var13 = 0.15978055;
            }
        } else {
            if (input[4] < 377.2652) {
                var13 = 0.039199233;
            } else {
                var13 = -0.07490858;
            }
        }
    } else {
        if (input[0] < 0.5090909) {
            if (input[8] < 6359.0) {
                var13 = 0.13759983;
            } else {
                var13 = -0.05405454;
            }
        } else {
            if (input[2] < 11.0) {
                var13 = -0.088644974;
            } else {
                var13 = 0.14133844;
            }
        }
    }
    var var14;
    if (input[8] < 5570.3335) {
        if (input[0] < 0.64) {
            if (input[4] < 374.32114) {
                var14 = -0.033322796;
            } else {
                var14 = 0.15074761;
            }
        } else {
            if (input[4] < 377.2652) {
                var14 = 0.035747174;
            } else {
                var14 = -0.068881884;
            }
        }
    } else {
        if (input[0] < 0.5090909) {
            if (input[8] < 6359.0) {
                var14 = 0.116467774;
            } else {
                var14 = -0.050336123;
            }
        } else {
            if (input[4] < 430.2517) {
                var14 = -0.09909824;
            } else {
                var14 = -0.040512193;
            }
        }
    }
    var var15;
    if (input[8] < 4407.5557) {
        if (input[0] < 0.6944444) {
            if (input[0] < 0.64444447) {
                var15 = 0.122305386;
            } else {
                var15 = -0.061202634;
            }
        } else {
            if (input[4] < 385.46545) {
                var15 = 0.09180179;
            } else {
                var15 = -0.08839813;
            }
        }
    } else {
        if (input[8] < 6262.0) {
            if (input[1] < 4.0) {
                var15 = 0.11091045;
            } else {
                var15 = -0.061959993;
            }
        } else {
            if (input[0] < 0.4) {
                var15 = -0.015283942;
            } else {
                var15 = -0.097062215;
            }
        }
    }
    var var16;
    if (input[3] < 517.99994) {
        if (input[3] < 326.00015) {
            if (input[8] < 6289.0) {
                var16 = 0.064368226;
            } else {
                var16 = -0.06513885;
            }
        } else {
            if (input[4] < 379.23676) {
                var16 = -0.14633453;
            } else {
                var16 = -0.07711171;
            }
        }
    } else {
        if (input[4] < 367.43634) {
            if (input[5] < 121.0) {
                var16 = 0.030510439;
            } else {
                var16 = 0.13474868;
            }
        } else {
            if (input[0] < 0.6282421) {
                var16 = 0.14192756;
            } else {
                var16 = -0.05483075;
            }
        }
    }
    var var17;
    if (input[8] < 6010.0) {
        if (input[1] < 4.0) {
            if (input[1] < 1.0) {
                var17 = -0.11910488;
            } else {
                var17 = 0.15542668;
            }
        } else {
            if (input[3] < 517.99994) {
                var17 = -0.08898544;
            } else {
                var17 = 0.019545328;
            }
        }
    } else {
        if (input[0] < 0.5090909) {
            if (input[7] < 693.5) {
                var17 = -0.028667688;
            } else {
                var17 = 0.27741048;
            }
        } else {
            if (input[2] < 11.0) {
                var17 = -0.089780115;
            } else {
                var17 = 0.13620357;
            }
        }
    }
    var var18;
    if (input[8] < 4407.5557) {
        if (input[0] < 0.7051282) {
            if (input[0] < 0.64444447) {
                var18 = 0.11475817;
            } else {
                var18 = -0.051834274;
            }
        } else {
            if (input[4] < 385.46545) {
                var18 = 0.089396834;
            } else {
                var18 = -0.07745342;
            }
        }
    } else {
        if (input[3] < 1094.0) {
            if (input[1] < 3.0) {
                var18 = -0.012453247;
            } else {
                var18 = -0.06862837;
            }
        } else {
            if (input[4] < 388.15225) {
                var18 = 0.12695883;
            } else {
                var18 = -0.07031915;
            }
        }
    }
    var var19;
    if (input[8] < 6010.0) {
        if (input[0] < 0.6282421) {
            if (input[4] < 370.9762) {
                var19 = -0.07218663;
            } else {
                var19 = 0.16382118;
            }
        } else {
            if (input[1] < 4.0) {
                var19 = 0.117785215;
            } else {
                var19 = -0.012581105;
            }
        }
    } else {
        if (input[0] < 0.5090909) {
            if (input[7] < 693.5) {
                var19 = -0.023761557;
            } else {
                var19 = 0.23795108;
            }
        } else {
            if (input[2] < 11.0) {
                var19 = -0.084919594;
            } else {
                var19 = 0.122768216;
            }
        }
    }
    var var20;
    if (input[3] < 517.99994) {
        if (input[3] < 453.9998) {
            if (input[8] < 6041.667) {
                var20 = 0.037767082;
            } else {
                var20 = -0.055192232;
            }
        } else {
            if (input[8] < 4248.6665) {
                var20 = -0.254215;
            } else {
                var20 = -0.100854315;
            }
        }
    } else {
        if (input[3] < 646.0001) {
            if (input[1] < 3.0) {
                var20 = 0.24605957;
            } else {
                var20 = 0.11596235;
            }
        } else {
            if (input[4] < 367.43634) {
                var20 = 0.06517418;
            } else {
                var20 = -0.054039128;
            }
        }
    }
    var var21;
    if (input[3] < 517.99994) {
        if (input[3] < 326.00015) {
            if (input[8] < 6358.0) {
                var21 = 0.048916876;
            } else {
                var21 = -0.052599933;
            }
        } else {
            if (input[0] < 0.69014084) {
                var21 = -0.049628146;
            } else {
                var21 = -0.12905332;
            }
        }
    } else {
        if (input[3] < 646.0001) {
            if (input[1] < 3.0) {
                var21 = 0.21785806;
            } else {
                var21 = 0.110521674;
            }
        } else {
            if (input[4] < 367.43634) {
                var21 = 0.060360212;
            } else {
                var21 = -0.04925621;
            }
        }
    }
    var var22;
    if (input[3] < 1094.0) {
        if (input[3] < 838.00006) {
            if (input[8] < 3384.0) {
                var22 = 0.11537081;
            } else {
                var22 = -0.029774869;
            }
        } else {
            if (input[4] < 385.90335) {
                var22 = -0.35328272;
            } else {
                var22 = -0.12356617;
            }
        }
    } else {
        if (input[0] < 0.6960784) {
            if (input[3] < 1158.0001) {
                var22 = 0.08867216;
            } else {
                var22 = -0.06481555;
            }
        } else {
            if (input[0] < 0.70247936) {
                var22 = 0.058127005;
            } else {
                var22 = 0.117891096;
            }
        }
    }
    var var23;
    if (input[3] < 517.99994) {
        if (input[3] < 453.9998) {
            if (input[8] < 6114.8887) {
                var23 = 0.03464095;
            } else {
                var23 = -0.04771673;
            }
        } else {
            if (input[0] < 0.46666667) {
                var23 = 0.116634086;
            } else {
                var23 = -0.11359048;
            }
        }
    } else {
        if (input[3] < 646.0001) {
            if (input[1] < 3.0) {
                var23 = 0.19960566;
            } else {
                var23 = 0.10483303;
            }
        } else {
            if (input[4] < 367.43634) {
                var23 = 0.054416772;
            } else {
                var23 = -0.042806752;
            }
        }
    }
    var var24;
    if (input[3] < 1094.0) {
        if (input[3] < 838.00006) {
            if (input[3] < 517.99994) {
                var24 = -0.039940532;
            } else {
                var24 = 0.039652992;
            }
        } else {
            if (input[4] < 371.95813) {
                var24 = -0.34504566;
            } else {
                var24 = -0.1307717;
            }
        }
    } else {
        if (input[0] < 0.6960784) {
            if (input[0] < 0.6597938) {
                var24 = 0.117791615;
            } else {
                var24 = -0.048584633;
            }
        } else {
            if (input[0] < 0.70247936) {
                var24 = 0.052224673;
            } else {
                var24 = 0.1153852;
            }
        }
    }
    var var25;
    if (input[8] < 6358.0) {
        if (input[0] < 0.64) {
            if (input[4] < 515.04803) {
                var25 = 0.11573459;
            } else {
                var25 = -0.07721384;
            }
        } else {
            if (input[1] < 4.0) {
                var25 = 0.07157976;
            } else {
                var25 = -0.019373713;
            }
        }
    } else {
        if (input[4] < 302.21844) {
            if (input[1] < 1.0) {
                var25 = -0.020713395;
            } else {
                var25 = 0.31010738;
            }
        } else {
            if (input[4] < 572.469) {
                var25 = -0.08927102;
            } else {
                var25 = 0.17485484;
            }
        }
    }
    var var26;
    if (input[3] < 1094.0) {
        if (input[3] < 838.00006) {
            if (input[8] < 3384.0) {
                var26 = 0.11155256;
            } else {
                var26 = -0.023666045;
            }
        } else {
            if (input[4] < 383.32562) {
                var26 = -0.25153467;
            } else {
                var26 = -0.11851569;
            }
        }
    } else {
        if (input[0] < 0.6960784) {
            if (input[4] < 360.4657) {
                var26 = 0.08764189;
            } else {
                var26 = -0.052343648;
            }
        } else {
            if (input[0] < 0.70247936) {
                var26 = 0.050059695;
            } else {
                var26 = 0.11389462;
            }
        }
    }
    var var27;
    if (input[8] < 6041.667) {
        if (input[0] < 0.64) {
            if (input[4] < 515.04803) {
                var27 = 0.13169312;
            } else {
                var27 = -0.10042083;
            }
        } else {
            if (input[4] < 434.8462) {
                var27 = -0.011002578;
            } else {
                var27 = 0.21298997;
            }
        }
    } else {
        if (input[0] < 0.36363637) {
            if (input[1] < 4.0) {
                var27 = 0.0013094004;
            } else {
                var27 = 0.28257957;
            }
        } else {
            if (input[4] < 572.469) {
                var27 = -0.07129174;
            } else {
                var27 = 0.13364625;
            }
        }
    }
    var var28;
    if (input[3] < 517.99994) {
        if (input[3] < 453.9998) {
            if (input[8] < 6359.0) {
                var28 = 0.02272095;
            } else {
                var28 = -0.046386052;
            }
        } else {
            if (input[0] < 0.46666667) {
                var28 = 0.10336719;
            } else {
                var28 = -0.10959792;
            }
        }
    } else {
        if (input[0] < 0.6282421) {
            if (input[4] < 458.82272) {
                var28 = 0.16887929;
            } else {
                var28 = -0.0528251;
            }
        } else {
            if (input[4] < 373.3758) {
                var28 = 0.043968182;
            } else {
                var28 = -0.05795443;
            }
        }
    }
    var var29;
    if (input[3] < 517.99994) {
        if (input[3] < 326.00015) {
            if (input[3] < 133.99994) {
                var29 = -0.014216565;
            } else {
                var29 = 0.10232524;
            }
        } else {
            if (input[0] < 0.69014084) {
                var29 = -0.028117973;
            } else {
                var29 = -0.12127238;
            }
        }
    } else {
        if (input[3] < 646.0001) {
            if (input[8] < 5924.667) {
                var29 = 0.12067473;
            } else {
                var29 = 0.0030666548;
            }
        } else {
            if (input[0] < 0.6282421) {
                var29 = 0.14113627;
            } else {
                var29 = -0.014449534;
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
