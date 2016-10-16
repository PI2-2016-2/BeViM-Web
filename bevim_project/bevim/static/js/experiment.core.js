var Timer = function(ref, time, toExecute, toStop, interval){
    this.ref = ref;
    this.endTime = {};
    this.timer = {};
    this.timeout = {};
    this.startTime = {};
    this.time = time;
    this.toExecute = toExecute;
    this.toStop = toStop;
    this.interval = interval;
}

Timer.prototype.start = function(){

    console.log("Starting timer " + this.ref);

    // Turning seconds into milliseconds
    var timeToStop = this.time * 1000;

    var outer = this;
    function stopFunction(){
        outer.endTime = outer.stop(); // Stop timer
        outer.toStop();
    }

    this.startTime = new Date();

    this.timer = setInterval(this.toExecute, this.interval);

    this.timeout = setTimeout(stopFunction, timeToStop);

    return this.startTime;
};

Timer.prototype.stop = function(){

    clearInterval(this.timer);

    var stopTime = new Date();

    return stopTime;
};

Timer.prototype.cancel = function(){

    this.endTime = this.stop();
    clearTimeout(this.timeout);

    var stopTime = new Date();

    return stopTime;
};

/**
 * Experiment Class
 */
var Experiment = function(onStart, onFinish, onTransition){
    this.startTime = {};
    this.endTime = {};
    this.timers = {};
    this.currentTimerIndex = 0;
    this.currentTimer = {};
    this.onStart = onStart;
    this.onFinish = onFinish;
    this.onTransition = onTransition;
}

Experiment.prototype.addTimer = function(timer){
    this.timers[timer.ref] = timer;
};

Experiment.prototype.start = function(){

    if(this.onStart != undefined){
        this.onStart();
    }

    this.startTime = this.startNextTimer();

    return this.startTime;
};

Experiment.prototype.prepare = function(prepareFunction){

    function extraFunctionDecorator(func, anotherFunc){
        return function(){
            func();
            anotherFunc();
        }
    }

    var curTimer = this.currentTimer;
    curTimer.toStop = extraFunctionDecorator(curTimer.toStop, prepareFunction);
};

Experiment.prototype.setNextTimer = function(){
    this.currentTimerIndex++;
    this.currentTimer = this.timers[this.currentTimerIndex];
};

Experiment.prototype.startNextTimer = function(){
    this.setNextTimer();

    var lastTimer = Object.keys(this.timers).length;
    var outer = this;
    if(this.currentTimerIndex < lastTimer){
        // In this case, the current timer is not the last one
        this.prepare(function(){
            outer.onTransition(outer);
        });
    }else{
        this.prepare(function(){
            // Setting the experiment end time on last timer stop
            outer.endTime = new Date();

            // Executing the user onFinish function
            outer.onFinish();
        });
    }
    var time = this.currentTimer.start();
    return time;
};

Experiment.prototype.continue = function(){
    this.startNextTimer();
};

Experiment.prototype.stop = function(stopFunction){
    this.currentTimer.cancel();
    this.onFinish();
    if(stopFunction){
        stopFunction();
    }
};