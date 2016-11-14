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

    if(this.onTransition != undefined){
        this.startTime = new Date();
        this.onTransition(this, true);
    }else{
        this.startTime = this.startNextTimer();
    }

    // outer = this;
    // (function(onTransition){
    //    onTransition = function(){
    //         onTransition();
    //    }
    // })(this.onTransition);



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

var ExperimentHistory = function(historyDiv){
    this.historyDiv = historyDiv;
}

ExperimentHistory.prototype.addEvent = function(content){
    var previousContent = $("#" + this.historyDiv).html();
    $("#" + this.historyDiv).html(previousContent + content);
};

ExperimentHistory.prototype.startExperimentEvent = function(startTime){

    if(startTime == undefined){
        startTime = new Date();
    }

    var hours = startTime.getHours();
    var minutes = startTime.getMinutes();
    var seconds = startTime.getSeconds();

    var startHtml = "\
    <article class='panel panel-success panel-outline'> \
        <div class='panel-heading icon'><i class='fa fa-play'></i></div> \
        <div class='panel-body'> Experiment started at " + hours + ":" + minutes + ":" + seconds +". \
        <strong>Firing Job 1...</strong>\
        </div> \
    </article>";

    return startHtml;
};

ExperimentHistory.prototype.pauseExperimentEvent = function(job, pauseTime){

    console.log("-----------------------------job on pause");
    console.log(job);

    if(pauseTime == undefined){
        pauseTime = new Date();
    }

    var hours = pauseTime.getHours();
    var minutes = pauseTime.getMinutes();
    var seconds = pauseTime.getSeconds();

    var pauseHtml = "\
    <article class='panel panel-warning panel-outline'> \
        <div class='panel-heading icon'><i class='fa fa-pause'></i></div> \
        <div class='panel-body'> <strong>Firing Job "+ job.order +"</strong>. Experiment paused at "
        + hours + ":" + minutes + ":" + seconds +" to wait for table reach " + job.frequency + " Hz.</div> \
    </article>";

    return pauseHtml;
};

ExperimentHistory.prototype.unpauseExperimentEvent = function(job, unpauseTime){

    if(unpauseTime == undefined){
        unpauseTime = new Date();
    }

    var hours = unpauseTime.getHours();
    var minutes = unpauseTime.getMinutes();
    var seconds = unpauseTime.getSeconds();

    var unpauseHtml = "\
    <article class='panel panel-primary panel-outline'> \
        <div class='panel-heading icon'><i class='fa fa-play-circle'></i></div> \
        <div class='panel-body'><strong>Initiating Job "+ job.order +"</strong>. Experiment unpaused at "
        + hours + ":" + minutes + ":" + seconds +", when table reached " + job.frequency + " Hz.</div> \
    </article>";

    unpauseHtml += "\
    <article class='panel panel-default panel-outline'> \
        <div class='panel-heading icon'><i class='fa fa-bolt'></i></div> \
        <div class='panel-body'>Vibrating at "+ job.frequency +"Hz for "
        + job.time + " seconds.</div> \
    </article>";

    return unpauseHtml;
};

ExperimentHistory.prototype.stopExperimentEvent = function(stopTime){

    if(stopTime == undefined){
        stopTime = new Date();
    }

    var hours = stopTime.getHours();
    var minutes = stopTime.getMinutes();
    var seconds = stopTime.getSeconds();

    var stopHtml = "\
    <article class='panel panel-danger panel-outline'> \
        <div class='panel-heading icon'><i class='fa fa-stop'></i></div> \
        <div class='panel-body'> Experiment stopped at "
        + hours + ":" + minutes + ":" + seconds +".</div> \
    </article>";

    return stopHtml;
};