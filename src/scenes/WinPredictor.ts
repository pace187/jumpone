
// Auto-generated XGBoost Model
// Used for Real-Time Win Probability Prediction in JumpOne
// Features expected in array order:
// [0] jumpSuccessRate, [1] jumpsFailed, [2] totalFalls, [3] maxFallDistance, [4] distancePerJump, [5] avgTimeBetweenJumps, [6] totalJumpsAttempted, [7] velocity_magnitude, [8] pos_x, [9] pos_y

function score(input) {
    var var0;
    if (input[5] < 1940.9534) {
        if (input[9] < 5981.333) {
            if (input[3] < 1414.0) {
                var0 = 0.16567886;
            } else {
                var0 = -0.091822825;
            }
        } else {
            if (input[0] < 0.7340425) {
                var0 = 0.042664267;
            } else {
                var0 = -0.17421906;
            }
        }
    } else {
        var0 = -0.19991912;
    }
    var var1;
    if (input[5] < 1940.9534) {
        if (input[9] < 5981.333) {
            if (input[3] < 1414.0) {
                var1 = 0.15017715;
            } else {
                var1 = -0.0828367;
            }
        } else {
            if (input[0] < 0.7315436) {
                var1 = 0.040385913;
            } else {
                var1 = -0.15551892;
            }
        }
    } else {
        var1 = -0.18180542;
    }
    var var2;
    if (input[5] < 1940.9534) {
        if (input[5] < 1388.168) {
            if (input[5] < 950.7902) {
                var2 = 0.12615389;
            } else {
                var2 = -0.06136344;
            }
        } else {
            if (input[0] < 0.7647059) {
                var2 = 0.16559614;
            } else {
                var2 = -0.15925194;
            }
        }
    } else {
        var2 = -0.16819775;
    }
    var var3;
    if (input[5] < 1940.9534) {
        if (input[9] < 5981.333) {
            if (input[5] < 1114.0625) {
                var3 = 0.040915105;
            } else {
                var3 = 0.16070475;
            }
        } else {
            if (input[0] < 0.6318408) {
                var3 = 0.070118435;
            } else {
                var3 = -0.10930125;
            }
        }
    } else {
        var3 = -0.15763076;
    }
    var var4;
    if (input[5] < 1940.9534) {
        if (input[5] < 1388.168) {
            if (input[5] < 950.7902) {
                var4 = 0.11285001;
            } else {
                var4 = -0.05743588;
            }
        } else {
            if (input[0] < 0.7647059) {
                var4 = 0.14562035;
            } else {
                var4 = -0.14180069;
            }
        }
    } else {
        var4 = -0.14921664;
    }
    var var5;
    if (input[5] < 1940.9534) {
        if (input[9] < 5981.333) {
            if (input[3] < 1414.0) {
                var5 = 0.11589821;
            } else {
                var5 = -0.07649181;
            }
        } else {
            if (input[1] < 13.0) {
                var5 = -0.08000448;
            } else {
                var5 = 0.12819909;
            }
        }
    } else {
        var5 = -0.14238429;
    }
    var var6;
    if (input[5] < 1940.9534) {
        if (input[5] < 1388.168) {
            if (input[5] < 950.7902) {
                var6 = 0.101194896;
            } else {
                var6 = -0.056618787;
            }
        } else {
            if (input[0] < 0.7647059) {
                var6 = 0.13289207;
            } else {
                var6 = -0.12999527;
            }
        }
    } else {
        var6 = -0.13674876;
    }
    var var7;
    if (input[5] < 1940.9534) {
        if (input[5] < 1388.168) {
            if (input[0] < 0.7009346) {
                var7 = -0.10057826;
            } else {
                var7 = 0.06030185;
            }
        } else {
            if (input[3] < 517.99994) {
                var7 = -0.041068163;
            } else {
                var7 = 0.13683213;
            }
        }
    } else {
        var7 = -0.13204063;
    }
    var var8;
    if (input[5] < 1940.9534) {
        if (input[9] < 5981.333) {
            if (input[5] < 1114.0625) {
                var8 = 0.02876914;
            } else {
                var8 = 0.1300429;
            }
        } else {
            if (input[0] < 0.652439) {
                var8 = 0.04912221;
            } else {
                var8 = -0.10092472;
            }
        }
    } else {
        var8 = -0.12806539;
    }
    var var9;
    if (input[5] < 1940.9534) {
        if (input[5] < 1388.168) {
            if (input[2] < 6.0) {
                var9 = 0.0326087;
            } else {
                var9 = -0.17006008;
            }
        } else {
            if (input[3] < 517.99994) {
                var9 = -0.03517387;
            } else {
                var9 = 0.12885265;
            }
        }
    } else {
        var9 = -0.12467903;
    }
    var var10;
    if (input[5] < 1940.9534) {
        if (input[9] < 5565.3335) {
            if (input[5] < 1033.3485) {
                var10 = 0.020802263;
            } else {
                var10 = 0.12318575;
            }
        } else {
            if (input[0] < 0.66887414) {
                var10 = 0.046410885;
            } else {
                var10 = -0.09403458;
            }
        }
    } else {
        var10 = -0.12177247;
    }
    var var11;
    if (input[5] < 1940.9534) {
        if (input[5] < 1388.168) {
            if (input[5] < 950.7902) {
                var11 = 0.08862865;
            } else {
                var11 = -0.054010462;
            }
        } else {
            if (input[0] < 0.7647059) {
                var11 = 0.11262734;
            } else {
                var11 = -0.11269987;
            }
        }
    } else {
        var11 = -0.11926154;
    }
    var var12;
    if (input[5] < 1940.9534) {
        if (input[9] < 5880.5557) {
            if (input[5] < 1114.0625) {
                var12 = 0.024554176;
            } else {
                var12 = 0.11810451;
            }
        } else {
            if (input[1] < 18.0) {
                var12 = -0.06725686;
            } else {
                var12 = 0.14208357;
            }
        }
    } else {
        var12 = -0.11708023;
    }
    var var13;
    if (input[5] < 1940.9534) {
        if (input[5] < 1388.168) {
            if (input[0] < 0.7009346) {
                var13 = -0.092374116;
            } else {
                var13 = 0.050477136;
            }
        } else {
            if (input[3] < 517.99994) {
                var13 = -0.030417075;
            } else {
                var13 = 0.11869415;
            }
        }
    } else {
        var13 = -0.11517596;
    }
    var var14;
    if (input[5] < 1940.9534) {
        if (input[9] < 5496.0) {
            if (input[5] < 1033.3485) {
                var14 = 0.016328905;
            } else {
                var14 = 0.11474114;
            }
        } else {
            if (input[0] < 0.66887414) {
                var14 = 0.041842174;
            } else {
                var14 = -0.08975599;
            }
        }
    } else {
        var14 = -0.11350644;
    }
    var var15;
    if (input[5] < 1940.9534) {
        if (input[5] < 1388.168) {
            if (input[5] < 950.7902) {
                var15 = 0.082044005;
            } else {
                var15 = -0.051785138;
            }
        } else {
            if (input[3] < 517.99994) {
                var15 = -0.02540769;
            } else {
                var15 = 0.11551471;
            }
        }
    } else {
        var15 = -0.112037055;
    }
    var var16;
    if (input[5] < 1940.9534) {
        if (input[1] < 1.0) {
            if (input[9] < 5981.333) {
                var16 = -0.28916946;
            } else {
                var16 = -0.09713101;
            }
        } else {
            if (input[0] < 0.65384614) {
                var16 = 0.112841524;
            } else {
                var16 = 0.022601176;
            }
        }
    } else {
        var16 = -0.110739425;
    }
    var var17;
    if (input[9] < 5200.333) {
        if (input[0] < 0.7058824) {
            if (input[5] < 1026.8572) {
                var17 = -0.10342355;
            } else {
                var17 = 0.09415785;
            }
        } else {
            if (input[3] < 1094.0) {
                var17 = 0.027004594;
            } else {
                var17 = 0.13434158;
            }
        }
    } else {
        if (input[4] < 435.8397) {
            if (input[1] < 37.0) {
                var17 = -0.092971645;
            } else {
                var17 = 0.080921106;
            }
        } else {
            if (input[1] < 5.0) {
                var17 = -0.019760238;
            } else {
                var17 = 0.12288876;
            }
        }
    }
    var var18;
    if (input[5] < 1940.9534) {
        if (input[5] < 1388.168) {
            if (input[5] < 950.7902) {
                var18 = 0.07733919;
            } else {
                var18 = -0.047788713;
            }
        } else {
            if (input[3] < 517.99994) {
                var18 = -0.023354588;
            } else {
                var18 = 0.111869894;
            }
        }
    } else {
        var18 = -0.10914411;
    }
    var var19;
    if (input[9] < 5129.5557) {
        if (input[0] < 0.7058824) {
            if (input[5] < 1026.8572) {
                var19 = -0.093402185;
            } else {
                var19 = 0.089706376;
            }
        } else {
            if (input[6] < 61.0) {
                var19 = 0.020567125;
            } else {
                var19 = 0.12853281;
            }
        }
    } else {
        if (input[0] < 0.676259) {
            if (input[5] < 1836.222) {
                var19 = 0.046875246;
            } else {
                var19 = -0.11918755;
            }
        } else {
            if (input[3] < 831.44446) {
                var19 = -0.10365689;
            } else {
                var19 = 0.12231737;
            }
        }
    }
    var var20;
    if (input[5] < 1940.9534) {
        if (input[1] < 1.0) {
            if (input[5] < 1502.3635) {
                var20 = -0.12082902;
            } else {
                var20 = 0.07999196;
            }
        } else {
            if (input[5] < 950.7902) {
                var20 = 0.12360244;
            } else {
                var20 = 0.018054469;
            }
        }
    } else {
        var20 = -0.107716896;
    }
    var var21;
    if (input[5] < 1940.9534) {
        if (input[5] < 1388.168) {
            if (input[4] < 369.8509) {
                var21 = 0.040811002;
            } else {
                var21 = -0.080880545;
            }
        } else {
            if (input[3] < 517.99994) {
                var21 = -0.019037237;
            } else {
                var21 = 0.109529436;
            }
        }
    } else {
        var21 = -0.10689991;
    }
    var var22;
    if (input[5] < 1940.9534) {
        if (input[5] < 1388.168) {
            if (input[2] < 6.0) {
                var22 = 0.018773912;
            } else {
                var22 = -0.14149243;
            }
        } else {
            if (input[3] < 517.99994) {
                var22 = -0.017173192;
            } else {
                var22 = 0.108555995;
            }
        }
    } else {
        var22 = -0.10616805;
    }
    var var23;
    if (input[9] < 5129.5557) {
        if (input[0] < 0.7058824) {
            if (input[5] < 1026.8572) {
                var23 = -0.08611851;
            } else {
                var23 = 0.08632006;
            }
        } else {
            if (input[2] < 3.0) {
                var23 = 0.017368494;
            } else {
                var23 = 0.12701446;
            }
        }
    } else {
        if (input[4] < 435.8397) {
            if (input[1] < 35.0) {
                var23 = -0.081651755;
            } else {
                var23 = 0.071406156;
            }
        } else {
            if (input[6] < 7.0) {
                var23 = -0.04508944;
            } else {
                var23 = 0.10089251;
            }
        }
    }
    var var24;
    if (input[5] < 1908.0083) {
        if (input[1] < 1.0) {
            if (input[5] < 1502.3635) {
                var24 = -0.106091194;
            } else {
                var24 = 0.08449333;
            }
        } else {
            if (input[5] < 950.7902) {
                var24 = 0.119236946;
            } else {
                var24 = 0.010176262;
            }
        }
    } else {
        if (input[1] < 44.0) {
            if (input[5] < 1940.9534) {
                var24 = -0.16457433;
            } else {
                var24 = -0.1054489;
            }
        } else {
            var24 = 0.09269612;
        }
    }
    var var25;
    if (input[5] < 1908.0083) {
        if (input[5] < 1429.852) {
            if (input[5] < 950.7902) {
                var25 = 0.06411528;
            } else {
                var25 = -0.041817192;
            }
        } else {
            if (input[0] < 0.7586207) {
                var25 = 0.0933403;
            } else {
                var25 = -0.08300897;
            }
        }
    } else {
        if (input[1] < 44.0) {
            if (input[5] < 1940.9534) {
                var25 = -0.15325926;
            } else {
                var25 = -0.10486406;
            }
        } else {
            var25 = 0.09128123;
        }
    }
    var var26;
    if (input[9] < 5014.0) {
        if (input[0] < 0.7058824) {
            if (input[5] < 1026.8572) {
                var26 = -0.08164316;
            } else {
                var26 = 0.08574658;
            }
        } else {
            if (input[2] < 3.0) {
                var26 = 0.011213973;
            } else {
                var26 = 0.12605785;
            }
        }
    } else {
        if (input[0] < 0.6769231) {
            if (input[1] < 1.0) {
                var26 = -0.07495729;
            } else {
                var26 = 0.058337297;
            }
        } else {
            if (input[3] < 831.44446) {
                var26 = -0.09225909;
            } else {
                var26 = 0.11146455;
            }
        }
    }
    var var27;
    if (input[5] < 1908.0083) {
        if (input[6] < 63.0) {
            if (input[3] < 838.00006) {
                var27 = -0.004012422;
            } else {
                var27 = -0.13980567;
            }
        } else {
            if (input[0] < 0.7) {
                var27 = -0.0045814677;
            } else {
                var27 = 0.121398866;
            }
        }
    } else {
        if (input[1] < 44.0) {
            if (input[5] < 1940.9534) {
                var27 = -0.14755224;
            } else {
                var27 = -0.104299806;
            }
        } else {
            var27 = 0.08850738;
        }
    }
    var var28;
    if (input[5] < 1908.0083) {
        if (input[5] < 1388.168) {
            if (input[4] < 367.18945) {
                var28 = 0.036004223;
            } else {
                var28 = -0.066396736;
            }
        } else {
            if (input[0] < 0.75) {
                var28 = 0.09054866;
            } else {
                var28 = -0.06045529;
            }
        }
    } else {
        if (input[1] < 44.0) {
            var28 = -0.10493491;
        } else {
            var28 = 0.087073736;
        }
    }
    var var29;
    if (input[3] < 1221.9999) {
        if (input[3] < 1158.0001) {
            if (input[3] < 1094.0) {
                var29 = -0.021754002;
            } else {
                var29 = 0.115127765;
            }
        } else {
            if (input[2] < 6.0) {
                var29 = -0.18193574;
            } else {
                var29 = -0.1526587;
            }
        }
    } else {
        if (input[2] < 6.0) {
            if (input[1] < 43.0) {
                var29 = 0.12169754;
            } else {
                var29 = 0.18658715;
            }
        } else {
            if (input[2] < 12.0) {
                var29 = -0.12447073;
            } else {
                var29 = 0.104945496;
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


// m2cgen generates 'function score(input) { ... }'
// It outputs raw margins (log-odds). We convert it to Probability [0, 1]
export function predictWinProbability(features) {
    const rawMargin = score(features); 
    let prob = 1 / (1 + Math.exp(-rawMargin));
    return prob;
}
