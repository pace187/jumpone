import { describe, it, expect } from 'vitest';

describe('Discrete-Jump Telemetry Tracking Simulation', () => {

    class MockTelemetryTracker {
        jumpInProgress = false;
        jumpStartX = 0;
        jumpStartY = 0;
        jumpStartTime = 0;
        landTime = 0;
        sessionStartTime = Date.now();
        
        succeededJumps = 0;
        failedJumps = 0;
        totalFallDistance = 0;
        maxFallDistance = 0;
        totalDistanceCovered = 0;
        totalPlanningTime = 0;
        totalJumpsAttempted = 0;

        // Simulate jumping
        simulateJump(x: number, y: number, time: number) {
            this.jumpInProgress = true;
            this.jumpStartX = x;
            this.jumpStartY = y;
            this.jumpStartTime = time;
            this.totalJumpsAttempted++;
            this.totalPlanningTime += (this.jumpStartTime - this.landTime);
        }

        // Simulate landing successfully
        simulateLand(x: number, y: number, time: number) {
            if (this.jumpInProgress) {
                this.succeededJumps++;
                const distance = Math.hypot(x - this.jumpStartX, y - this.jumpStartY);
                this.totalDistanceCovered += distance;
                this.jumpInProgress = false;
                this.landTime = time;
            }
        }

        // Simulate falling to death
        simulateFallDeath(deathY: number, time: number) {
            if (this.jumpInProgress) {
                this.failedJumps++;
                const currentFallDistance = Math.abs(deathY - this.jumpStartY);
                this.totalFallDistance += currentFallDistance;
                if (currentFallDistance > this.maxFallDistance) {
                    this.maxFallDistance = currentFallDistance;
                }
                this.jumpInProgress = false;
                this.landTime = time; // Respawn reset
            }
        }

        aggregateSessionData(endTime: number) {
            const jumpSuccessRate = this.totalJumpsAttempted > 0 ? (this.succeededJumps / this.totalJumpsAttempted) : 0;
            const avgFallDistance = this.failedJumps > 0 ? (this.totalFallDistance / this.failedJumps) : 0;
            const distancePerJump = this.totalJumpsAttempted > 0 ? (this.totalDistanceCovered / this.totalJumpsAttempted) : 0;
            const avgTimeBetweenJumps = this.totalJumpsAttempted > 0 ? (this.totalPlanningTime / this.totalJumpsAttempted) : 0;
            const sessionDuration_sec = (endTime - this.sessionStartTime) / 1000;

            return {
                jumpSuccessRate,
                jumpsFailed: this.failedJumps,
                avgFallDistance,
                maxFallDistance: this.maxFallDistance,
                distancePerJump,
                avgTimeBetweenJumps,
                totalJumpsAttempted: this.totalJumpsAttempted,
                sessionDuration_sec
            };
        }
    }

    it('should correctly track a Skilled Player profile', () => {
        const tracker = new MockTelemetryTracker();
        const start = Date.now();
        tracker.sessionStartTime = start;
        tracker.landTime = start; // Emulate initial spawn

        // Skilled player: Fast planning time, large accurate jumps, no deaths
        
        // Jump 1
        tracker.simulateJump(0, 6500, start + 500); // 500ms planning
        tracker.simulateLand(300, 6400, start + 1000); // 316.2 distance

        // Jump 2
        tracker.simulateJump(300, 6400, start + 1300); // 300ms planning
        tracker.simulateLand(600, 6200, start + 2000); // 360.5 distance

        // Jump 3
        tracker.simulateJump(600, 6200, start + 2200); // 200ms planning
        tracker.simulateLand(1000, 6000, start + 3000); // 447.2 distance

        const result = tracker.aggregateSessionData(start + 3000);

        expect(result.jumpSuccessRate).toBe(1); // 100%
        expect(result.jumpsFailed).toBe(0);
        expect(result.avgFallDistance).toBe(0);
        expect(result.totalJumpsAttempted).toBe(3);
        
        // Distances: Math.hypot(300, 100) + Math.hypot(300, 200) + Math.hypot(400, 200)
        // Avg: (316.22 + 360.55 + 447.21) / 3 = ~374.66
        expect(result.distancePerJump).toBeCloseTo(374.66, 1);
        
        // Planning times: 500 + 300 + 200 = 1000. Avg: 333.33ms
        expect(result.avgTimeBetweenJumps).toBeCloseTo(333.33, 1);
    });

    it('should correctly track a Struggling Player profile', () => {
        const tracker = new MockTelemetryTracker();
        const start = Date.now();
        tracker.sessionStartTime = start;
        tracker.landTime = start; // Emulate initial spawn

        // Struggling player: Long planning times, small jumps, multiple deaths
        
        // Jump 1 (Success)
        tracker.simulateJump(0, 6500, start + 3000); // 3000ms planning
        tracker.simulateLand(100, 6500, start + 3500); // 100 distance

        // Jump 2 (Fail - falls into void > 7000)
        tracker.simulateJump(100, 6500, start + 8500); // 5000ms planning
        tracker.simulateFallDeath(7500, start + 9500); // Fall distance = abs(7500 - 6500) = 1000

        // Jump 3 (Fail - falls worse)
        tracker.simulateJump(100, 6500, start + 11500); // 2000ms planning 
        tracker.simulateFallDeath(8000, start + 13000); // Fall distance = abs(8000 - 6500) = 1500

        const result = tracker.aggregateSessionData(start + 13000);

        // 1 success out of 3 attempts
        expect(result.jumpSuccessRate).toBeCloseTo(0.33, 2); 
        expect(result.jumpsFailed).toBe(2);
        
        // Fall Distances: 1000, 1500. Avg: 1250, Max: 1500
        expect(result.avgFallDistance).toBe(1250);
        expect(result.maxFallDistance).toBe(1500);

        // Distance: Only 1 successful jump landing evaluated: 100 distance over 3 attempts = 33.33 average
        expect(result.distancePerJump).toBeCloseTo(33.33, 1);
        
        // Planning times: 3000 + 5000 + 2000 = 10000. Avg: 3333.33ms
        expect(result.avgTimeBetweenJumps).toBeCloseTo(3333.33, 1);
    });

});
