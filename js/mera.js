/* MERA adaptive self-checks (adult and child).
   One question at a time; each next question depends only on the answers so far.
   Nothing is stored or sent. Rules follow the MERA build spec (November 2026). */
(function () {
  "use strict";
  var box = document.getElementById("mera-flow");
  if (!box) return;
  var TOOL = box.getAttribute("data-tool");

  /* ---------- helpers ---------- */
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); }
  function inSet(v, s) { return v != null && s.indexOf(v) !== -1; }
  function has(arr, v) { return Array.isArray(arr) && arr.indexOf(v) !== -1; }
  var L = "abcdefghij";

  /* ---------- WHO growth (LMS tables in js/who.js) ---------- */
  function lms(key, months) {
    var T = window.WHO_LMS && window.WHO_LMS[key]; if (!T) return null;
    var m = Math.min(Math.max(months, 24), 216), i = Math.floor(m) - 24, f = m - Math.floor(m);
    var a = T[i], b = T[Math.min(i + 1, T.length - 1)];
    return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f];
  }
  function zs(x, p) { return p[0] === 0 ? Math.log(x / p[1]) / p[2] : (Math.pow(x / p[1], p[0]) - 1) / (p[0] * p[2]); }
  function pctl(z) {
    var t = 1 / (1 + 0.2316419 * Math.abs(z)), d = 0.3989423 * Math.exp(-z * z / 2);
    var p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
    return Math.round((z > 0 ? 1 - p : p) * 100);
  }
  function ord(n) { if (n < 1) return "below the 1st"; if (n > 99) return "above the 99th"; var s = (n % 100 > 10 && n % 100 < 14) ? "th" : ({1: "st", 2: "nd", 3: "rd"}[n % 10] || "th"); return "the " + n + s; }

  /* ---------- state ---------- */
  var A = {};          // answers by question id
  var path = [];       // ids in the order answered
  var extra = null;    // adult: optional questions asked after the result
  var frozen = null;   // adult: result fixed before optional questions

  /* =====================================================================
     ADULT
     ===================================================================== */
  var AQ = {
    age: {type: "number", label: "Age", q: "How old are you?", fields: [{id: "y", label: "Age (years)", min: 1, max: 110}]},
    q1: {label: "Snoring", q: "How loud is the snoring?", opts: ["Can be heard from another room", "Can be heard in the bedroom", "No snoring", "I sleep alone, or I don't know"]},
    q2: {label: "Breathing pauses", q: "Have you or anyone else noticed pauses in your breathing during sleep?", opts: ["I wake up choking or gasping", "My partner or room-mate has seen me stop breathing", "The snoring gets louder and softer without me changing position", "None of these", "I sleep alone, or I don't know"]},
    q3: {label: "Sleepy while driving", q: "Sleepiness while driving in the daytime", opts: ["I have fallen asleep while the vehicle was moving", "I have felt sleepy while driving", "I have fallen asleep while stopped at a traffic signal", "I have fallen asleep while briefly stopped", "Never sleepy while driving", "I don't drive"]},
    q4: {label: "While talking", q: "While talking with someone during the day", opts: ["I have dozed off", "I usually feel sleepy", "Never sleepy"]},
    q5: {label: "In meetings", q: "In a meeting or discussion during the day", opts: ["I have dozed off", "I usually feel sleepy", "Never sleepy"]},
    q6: {label: "On video calls", q: "On a video call (Zoom, Meet) during the day", opts: ["I have dozed off", "I usually feel sleepy", "Never sleepy", "I don't use video calls"]},
    q7: {label: "Watching the phone", q: "Watching your phone while sitting", opts: ["I have dozed off while scrolling reels or shorts", "I have dozed off while watching long videos", "Never dozed off", "I don't watch videos or social media on my phone"]},
    q8: {label: "In an audience", q: "Sitting in an audience during the day (church, temple, programme, TV, movie, presentation)", opts: ["I have dozed off", "I usually feel sleepy", "Never sleepy"]},
    q9: {label: "Sitting idle", q: "Sitting idle during the day", opts: ["I have dozed off", "I usually feel sleepy", "Never sleepy"]},
    q10: {label: "On waking", q: "When you wake up in the morning", opts: ["I feel I haven't slept enough and want to go back to sleep", "I feel tired but not sleepy", "I feel fresh and energetic"]},
    q11: {label: "Morning headache", q: "Do you wake up with a headache?", opts: ["Most mornings", "Sometimes", "No"]},
    q12: {label: "Diabetes", q: "Diabetes", opts: ["Not controlled, on more than 2 medicines", "Not controlled, on 1 medicine", "Controlled", "I don't have diabetes"]},
    q13: {label: "Blood pressure", q: "High blood pressure", opts: ["Not controlled, on more than 2 medicines", "Not controlled, on 1 medicine", "Controlled", "I don't have high blood pressure"]},
    q14: {label: "Interest in sex", q: "Interest in sex (optional)", opts: ["Not interested", "Reduced", "Normal", "Prefer not to say"]},
    q15: {type: "bmi", label: "Weight", q: "Your weight",
      hint: "Enter your height and weight, or choose a description if you don't know them.",
      opts: ["I'm clearly obese", "I'm overweight", "I'm a little overweight", "My weight is normal"]}
  };
  var A_ORDER = ["age", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12", "q13", "q14", "q15"];

  function aWeight() { // a = BMI over 30 / obese, b = 25-30 / overweight, c = below 25
    var w = A.q15; if (!w) return null;
    if (w.bmi) return w.bmi > 30 ? "a" : w.bmi >= 25 ? "b" : "c";
    return w.v === "a" ? "a" : w.v === "b" ? "b" : "c";
  }
  function aRouteA() { return inSet(A.q2, "ab") || (A.q2 === "c" && A.q1 === "a"); }
  function aDozing() {
    var n = 0;
    if (inSet(A.q3, "abcd")) n++;
    ["q4", "q5", "q6", "q7"].forEach(function (k) { if (A[k] === "a") n++; });
    return n;
  }
  function aMarkers() {
    var m = [];
    if (A.q1 === "a") m.push("Loud snoring");
    if (A.q2 === "c") m.push("Snoring that rises and falls");
    if (aDozing() >= 2) m.push("Dozing off during the day");
    if (A.q10 === "a" || (A.q10 === "b" && A.q11 === "a")) m.push("Unrefreshing sleep");
    if (inSet(aWeight(), "ab")) m.push("Weight (BMI 25 or above)");
    if (inSet(A.q13, "ab")) m.push("Uncontrolled blood pressure");
    return m;
  }
  function adultNext() {
    if (!A.age) return "age";
    if (!A.q2) return "q2";
    if (A.q2 === "c" && !A.q1) return "q1";
    if (aRouteA()) {
      var ra = ["q3", "q15", "q13"];
      for (var i = 0; i < ra.length; i++) if (!A[ra[i]]) return ra[i];
      return null;
    }
    var seq = [];
    if (A.q2 !== "e") seq.push("q1");
    seq.push("q3", "q4", "q5", "q6", "q7", "q10");
    for (var j = 0; j < seq.length; j++) {
      if (!A[seq[j]]) return seq[j];
      if (aMarkers().length >= 3) return null;
    }
    if (inSet(A.q10, "ab") && !A.q11) return "q11";
    if (aMarkers().length >= 3) return null;
    if (!A.q15) return "q15";
    if (aMarkers().length >= 3) return null;
    if (!A.q13) return "q13";
    if (aMarkers().length === 0 && inSet(A.q1, "ab")) {
      if (!A.q8) return "q8";
      if (A.q8 !== "a" && !A.q9) return "q9";
    }
    return null;
  }
  function adultResult() {
    var r = {adds: []}, age = A.age && A.age.y;
    if (aRouteA()) {
      var w = aWeight();
      if (inSet(w, "ab") && inSet(A.q13, "ab")) {
        r.level = "high"; r.title = "Very high risk of sleep apnoea";
        r.text = "Please see a doctor soon for a sleep study." + (age > 40 ? " Together with your blood pressure and weight, this raises your risk of heart disease and stroke." : "");
      } else {
        r.level = "high"; r.title = "High risk of sleep apnoea";
        r.text = "Please book a sleep study. Your doctor may advise CPAP or further tests.";
      }
      if (w === "c") r.adds.push("Because your weight is normal, an ENT check of your nose and throat, and possibly sleep endoscopy (DISE), can show where your airway narrows.");
      r.why = A.q2 === "c" ? "Loud snoring that rises and falls" : "Breathing pauses or choking during sleep";
    } else {
      var m = aMarkers();
      r.why = m.join(", ");
      if (m.length >= 3) { r.level = "high"; r.title = "High risk of sleep apnoea"; r.text = "Please book a sleep study. Your doctor may advise CPAP or further tests."; }
      else if (m.length >= 1 || (inSet(A.q1, "ab") && (A.q8 === "a" || A.q9 === "a"))) {
        r.level = "mid"; r.title = "Sleep apnoea is possible";
        r.text = "Consider a sleep study, and a check with an ENT doctor or a pulmonologist (chest physician).";
        if (!m.length) r.why = "Snoring, with dozing off when sitting";
      } else { r.level = "low"; r.title = "Sleep apnoea is less likely"; r.text = "Sleep apnoea is less likely from your answers. If you still snore loudly or feel tired, see a doctor."; }
      if (A.q2 === "d" && A.q1 === "c" && aDozing() >= 2) r.adds.push("Sleep apnoea is less likely, but your daytime sleepiness needs a doctor's check.");
    }
    if (inSet(A.q3, "ab")) r.urgent = "Please avoid driving until you've been assessed. Falling asleep at the wheel is a serious risk to you and others.";
    else if (inSet(A.q3, "cd")) r.urgent = "Dozing at traffic stops is a warning sign. Please be careful and get assessed soon.";
    if (A.q2 === "e") r.adds.push("No one has watched you sleep, so breathing pauses can't be ruled out. A phone recording of your snoring overnight can help your doctor.");
    return r;
  }

  /* =====================================================================
     CHILD
     ===================================================================== */
  var CQ = {
    age: {type: "number", label: "Age", q: "How old is your child?", hint: "For children aged 2 to 17 years.",
      fields: [{id: "y", label: "Years", min: 0, max: 30}, {id: "m", label: "Months", min: 0, max: 11, optional: true}]},
    sex: {label: "Sex", q: "Your child is a", opts: ["Boy", "Girl"]},
    hw: {type: "number", label: "Height and weight", q: "Your child's height and weight", hint: "Enter them if you know them; they're checked against the WHO growth charts. Skip if you don't know.",
      fields: [{id: "cm", label: "Height (cm)", min: 45, max: 210}, {id: "kg", label: "Weight (kg)", min: 3, max: 200}], skip: "I don't know"},
    concerns: {type: "multi", label: "Your concerns", q: "What worries you about your child?", hint: "Tick all that apply.",
      opts: ["Snoring or breathing at night", "Mouth breathing or a blocked nose", "Ear infections or hearing", "Frequent colds or sore throats", "Growth or eating", "Nothing specific, just checking"], none: "f"},
    q1: {label: "Snoring", q: "Does your child snore?", opts: ["Always", "Only in certain sleeping positions", "Only when they have a cold or infection", "No snoring"]},
    q2: {label: "Breathing stops", q: "Have you seen your child's breathing stop or get blocked during sleep?", opts: ["Yes, many times", "Yes, a few times", "Not seen"]},
    q3: {label: "Laboured breathing", q: "Have you seen your child breathe with effort (laboured breathing) during sleep?", opts: ["Yes, even with the mouth open and without a cold", "Yes, with the mouth closed, without a cold", "Yes, only during a cold", "Not seen"]},
    q6: {label: "Mouth open in sleep", q: "Does your child sleep with the mouth open?", opts: ["Yes, always", "Only during a cold", "No"]},
    q7: {label: "Mouth breathing awake", q: "Does your child breathe through the mouth while awake?", opts: ["Yes, always", "Only during a cold", "No"]},
    q8: {label: "Bedwetting", q: "Does your child wet the bed during sleep?", opts: ["Yes", "No"]},
    q9: {label: "Restlessness", q: "Is your child restless?", opts: ["Always running around, won't sit still for long (except for a favourite programme)", "Hard to get them to sit and listen or study", "No such problems"]},
    q10: {label: "Yawning", q: "Does your child yawn repeatedly?", opts: ["Always", "Occasionally", "Never"]},
    q11: {label: "Sleeping in class", q: "Does your child fall asleep in class?", opts: ["Always", "Occasionally", "Never", "Not in school yet"]},
    q12: {label: "Sleeping at video games", q: "Does your child fall asleep while playing video games?", opts: ["Always", "Occasionally", "Never", "Doesn't play video games"]},
    q13: {label: "School performance", q: "How is your child doing at school?", opts: ["Poor", "Below average", "Average or above"]},
    q14: {label: "Weight", q: "Your child's weight", opts: ["Not gaining weight, even though they eat enough", "Not gaining weight, and they don't eat enough", "Normal weight", "A little heavier than children of the same age", "Clearly heavier than children of the same age"]},
    q15: {label: "Height", q: "Compared with other children of the same age, your child is", opts: ["(very short, from the WHO check)", "Among the shortest", "Shorter than average", "Height is OK"], from: 1},
    q16: {type: "multi", label: "Face", q: "Look at your child's face. Do you notice any of these?", hint: "Tick all that apply.",
      opts: ["Mouth usually hangs open, lips apart", "Upper front teeth stick out, or teeth are crowded", "Long, narrow face with a tired look", "Small chin, or chin set back", "None of these"], none: "e"},
    q17: {fig: true, label: "Tonsils (torch check)", q: "Shine a torch into your child's open mouth while they say \"aah\". The tonsils (the lumps on either side at the back) are:", opts: ["So big they touch or nearly touch in the middle", "Clearly large, filling half the space", "Small or hard to see", "Removed earlier, or I couldn't see"]},
    q18: {label: "Ear infections", q: "Ear infections (ear pain with fever, or pus from the ear):", opts: ["3 or more in the last 6 months", "4 or more in the last year", "2 or 3 in the last year", "0 or 1 in the last year"]},
    q19: {type: "multi", label: "Hearing", q: "Hearing: have you or a teacher noticed any of these?", hint: "Tick all that apply.",
      opts: ["Often asks \"what?\" or needs things repeated", "Keeps the TV or phone volume high", "Doesn't respond when called from another room", "None of these"], none: "d"},
    q20: {label: "Colds and sore throats", q: "Colds and sore throats in the last year", opts: ["Sore throat or tonsillitis 5 or more times", "Blocked or running nose most of the year", "The usual number of colds", "Rarely ill"]},
    q21: {label: "Adenoid X-ray or endoscopy", q: "Has a doctor checked your child's adenoids with an X-ray or a nasal endoscopy?", opts: ["Yes, and they said how much it's blocked", "Yes, they said the adenoids are enlarged, but gave no number", "Yes, and they said it's normal", "No, or I don't know"]},
    q21g: {label: "How much blocked", q: "What did the doctor say?", opts: ["Under 25% blocked, or grade 1", "25 to 50% blocked, or grade 2", "50 to 75% blocked, or grade 3", "Over 75% blocked, or grade 4"]},
    q21t: {label: "When checked", q: "When was the X-ray or endoscopy done?", opts: ["Within the last 6 months", "6 to 12 months ago", "More than a year ago"]},
    q22: {label: "Blocked-nose voice", q: "Does your child talk as if the nose is blocked?", opts: ["Always", "Only with a cold", "No"]},
    q23: {label: "Speech", q: "Is your child's speech behind other children of the same age?", opts: ["Clearly behind", "A little behind", "No"]},
    q24: {label: "Tonsil size (doctor)", q: "Has a doctor told you the size of the tonsils?", opts: ["Large (grade 3 or 4), or touching", "Normal size (grade 1 or 2)", "Not told"]}
  };


  /* Tonsil size drawing for Q17: three mouth views, largest first, matching the answer order */
  function tonsilFigure() {
    function panel(x, rx, cx, label) {
      var lx = x + cx, rxx = x + 120 - cx;
      return '<g transform="translate(' + x + ',0)">' +
        '<ellipse cx="60" cy="62" rx="52" ry="48" fill="#f4c2b5" stroke="#b5524a" stroke-width="4"/>' +
        '<path d="M22 100 Q22 26 60 22 Q98 26 98 100 Z" fill="#f7d0c6"/>' +
        '<ellipse cx="60" cy="70" rx="24" ry="34" fill="#6b1e24"/>' +
        '<path d="M36 100 Q34 44 40 34" fill="none" stroke="#d9867c" stroke-width="3"/>' +
        '<path d="M84 100 Q86 44 80 34" fill="none" stroke="#d9867c" stroke-width="3"/>' +
        '</g>' +
        '<ellipse cx="' + lx + '" cy="70" rx="' + rx + '" ry="19" fill="#e8908a" stroke="#b5524a" stroke-width="1.5"/>' +
        '<ellipse cx="' + rxx + '" cy="70" rx="' + rx + '" ry="19" fill="#e8908a" stroke="#b5524a" stroke-width="1.5"/>' +
        '<g transform="translate(' + x + ',0)">' +
        '<path d="M54 30 Q53 48 60 54 Q67 48 66 30 Z" fill="#e58f86" stroke="#b5524a" stroke-width="1.2"/>' +
        '<ellipse cx="60" cy="104" rx="46" ry="16" fill="#e07a7a"/>' +
        '<path d="M60 92 L60 112" stroke="#c45f5f" stroke-width="1.5"/>' +
        '<text x="60" y="134" text-anchor="middle" font-size="13" font-weight="600" fill="#18261f">' + label + '</text>' +
        '</g>';
    }
    return '<figure class="flow-fig" aria-label="Drawing of tonsil sizes: very large tonsils touching in the middle, large tonsils filling half the space, and small tonsils">' +
      '<svg viewBox="0 0 380 142" role="img" xmlns="http://www.w3.org/2000/svg">' +
      panel(0, 22, 39, "Touching") + panel(130, 14, 37, "Half the space") + panel(260, 7, 37, "Small") +
      '</svg><figcaption>What you might see when your child says "aah". The tonsils are the pink lumps on each side of the dark throat.</figcaption></figure>';
  }

  function cAge() { var a = A.age; return a ? a.y + (a.m || 0) / 12 : null; }
  function cGrowth() {
    var g = {measured: false, abnormal: false, thrive: false, text: "", flags: []};
    var a = cAge(), hw = A.hw, s = A.sex;
    if (hw && hw.cm && s) {
      g.measured = true;
      var months = a * 12, sx = s === "a" ? "b" : "g";
      var hz = zs(hw.cm, lms(sx + "h", months)), parts = [];
      parts.push("height " + ord(pctl(hz)) + " percentile");
      if (hz < -3) { g.flags.push("very short for age"); g.abnormal = g.thrive = true; }
      else if (hz < -2) { g.flags.push("short for age"); g.abnormal = g.thrive = true; }
      else if (hz < -1) g.flags.push("height below average");
      if (hw.kg) {
        var bmi = hw.kg / Math.pow(hw.cm / 100, 2), bz = zs(bmi, lms(sx + "b", months)), u5 = a < 5;
        var obese = u5 ? bz > 3 : bz > 2, over = u5 ? bz > 2 : bz > 1;
        parts.push("BMI " + bmi.toFixed(1) + ", " + ord(pctl(bz)) + " percentile");
        if (obese) { g.flags.push("obese"); g.abnormal = true; }
        else if (over) g.flags.push("overweight");
        else if (bz < -2) { g.flags.push("thin for age"); g.abnormal = g.thrive = true; g.thin = true; }
      }
      g.text = "WHO check: " + parts.join("; ") + ".";
    }
    if (A.q14 === "a") { g.flags.push("not gaining weight despite eating"); g.abnormal = g.thrive = true; }
    else if (A.q14 === "b") g.flags.push("not gaining weight, eats little");
    else if (A.q14 === "e") { g.flags.push("clearly heavier than other children"); g.abnormal = true; }
    else if (A.q14 === "d") g.flags.push("a little heavier than other children");
    if (A.q15 === "b") { g.flags.push("among the shortest"); g.abnormal = g.thrive = true; }
    else if (A.q15 === "c") g.flags.push("shorter than average");
    return g;
  }
  function cMod() {
    var c = A.concerns || [];
    return {
      osa: has(c, "a") || inSet(A.q1, "ab") || A.q6 === "a",
      ears: has(c, "c") || (Array.isArray(A.q19) && A.q19.some(function (x) { return x !== "d"; }))
    };
  }
  function cApplies(id) {
    var a = cAge();
    if (id === "q8" || id === "q13") return a >= 5;
    if (id === "q9") return a >= 4 && a <= 12;
    if (id === "q23") return a < 5;
    return true;
  }
  function cDaytime() {
    var n = 0;
    if (A.q10 === "a") n++;
    if (inSet(A.q11, "ab")) n++;
    if (inSet(A.q12, "ab")) n++;
    if (A.q13 === "a" && cApplies("q13")) n++;
    return n;
  }
  function cOsaMarkers() {
    var m = [];
    if (inSet(A.q1, "ab")) m.push("Snoring");
    if (inSet(A.q3, "ab")) m.push("Laboured breathing in sleep");
    if (A.q6 === "a" || A.q7 === "a") m.push("Mouth breathing");
    if (A.q17 === "a" || A.q24 === "a") m.push("Very large tonsils");
    if (has(A.q16, "d")) m.push("Small chin");
    if (cGrowth().abnormal) m.push("Growth affected");
    if (inSet(A.q9, "ab") && cApplies("q9")) m.push("Restless or hyperactive");
    if (cDaytime() >= 2) m.push("Daytime sleepiness");
    if (A.q8 === "a" && cApplies("q8")) m.push("Bedwetting");
    return m;
  }
  function cAdenoidRecent() { return A.q21t === "a"; }
  function cAdenoidConfirmedBig() { return cAdenoidRecent() && ((A.q21 === "a" && inSet(A.q21g, "cd")) || A.q21 === "b"); }
  function childNext() {
    var order = ["age", "sex", "hw", "concerns", "q1", "q6", "q17", "q19", "q21"];
    for (var i = 0; i < order.length; i++) if (A[order[i]] == null) return order[i];
    if (A.q21 === "a" && !A.q21g) return "q21g";
    if (inSet(A.q21, "abc") && !A.q21t) return "q21t";
    var g = cGrowth();
    if (!A.q14 && (!g.measured || (A.hw && !A.hw.kg) || g.thin)) return "q14";
    if (!A.q15 && !g.measured) return "q15";
    var mod = cMod();
    if (mod.osa) {
      if (!A.q2) return "q2";
      if (!A.q3) return "q3";
      if (A.q2 === "c") {
        var seq = ["q7", "q16", "q9", "q10", "q11", "q12", "q13", "q8"];
        for (var j = 0; j < seq.length; j++) {
          if (cOsaMarkers().length >= 3) break;
          if (cApplies(seq[j]) && A[seq[j]] == null) return seq[j];
        }
      }
    }
    if (!cAdenoidConfirmedBig()) {
      var ad = ["q7", "q16", "q20", "q22"];
      for (var k = 0; k < ad.length; k++) if (A[ad[k]] == null) return ad[k];
    } else if (!A.q20) return "q20";
    if (mod.ears) {
      if (!A.q18) return "q18";
      if (cApplies("q23") && !A.q23) return "q23";
    } else if (!A.q18) {
      var pre = childResult();
      if (pre.adenoid.lvl === "high" || pre.osaKey === "HIGH") return "q18";
    }
    if (inSet(A.q17, "abd") && !A.q24) return "q24";
    return null;
  }
  function childResult() {
    var a = cAge(), g = cGrowth(), mod = cMod(), R = {};
    /* 1. Adenoids */
    var adCount = 0;
    if (A.q6 === "a") adCount++;
    if (A.q7 === "a") adCount++;
    if (Array.isArray(A.q16) && A.q16.filter(function (x) { return "abcd".indexOf(x) !== -1; }).length >= 2) adCount++;
    if (A.q20 === "b") adCount++;
    if (A.q22 === "a") adCount++;
    var grades = {a: "under 25% blocked (grade 1)", b: "25 to 50% blocked (grade 2)", c: "50 to 75% blocked (grade 3)", d: "over 75% blocked (grade 4)"};
    var when = {a: "within the last 6 months", b: "6 to 12 months ago", c: "more than a year ago"};
    var docLine = A.q21 === "a" ? "Doctor's finding (" + when[A.q21t] + "): " + grades[A.q21g] + "."
      : A.q21 === "b" ? "Doctor's finding (" + when[A.q21t] + "): enlarged, no grade given."
      : A.q21 === "c" ? "Doctor's finding (" + when[A.q21t] + "): normal." : "";
    var ad;
    if (cAdenoidRecent() && A.q21 === "a") ad = A.q21g === "a" ? {lvl: "low", t: "Not significantly enlarged (confirmed by doctor)"} : A.q21g === "b" ? {lvl: "mid", t: "Mildly enlarged (confirmed by doctor)"} : {lvl: "high", t: "Enlarged (confirmed by doctor)"};
    else if (cAdenoidRecent() && A.q21 === "b") ad = {lvl: "high", t: "Enlarged (confirmed by doctor)"};
    else if (cAdenoidRecent() && A.q21 === "c") ad = adCount >= 3 ? {lvl: "mid", t: "Reported normal, but symptoms suggest a recheck is worthwhile"} : {lvl: "low", t: "Not significantly enlarged (confirmed by doctor)"};
    else ad = adCount >= 3 ? {lvl: "high", t: "Likely enlarged"} : adCount >= 1 ? {lvl: "mid", t: "Possibly enlarged"} : {lvl: "low", t: "Unlikely to be enlarged"};
    if (A.q21 === "c" && !cAdenoidRecent() && adCount >= 3) ad.note = "The earlier X-ray or endoscopy was normal, but your child's symptoms suggest the adenoids are worth rechecking.";
    ad.doc = docLine;
    R.adenoid = ad;

    /* 2. Complications */
    var osa;
    if (!mod.osa) osa = {lvl: "low", t: "Sleep apnoea unlikely (no snoring or night breathing problems reported)"};
    else if (inSet(A.q2, "ab")) {
      if (inSet(A.q3, "ab") && A.q1 === "a") osa = g.abnormal ? {lvl: "high", t: "High risk of sleep apnoea, and it may already be affecting growth", key: "HIGH"} : {lvl: "high", t: "High risk of sleep apnoea", key: "HIGH"};
      else osa = {lvl: "mid", t: "Sleep apnoea likely (breathing pauses seen)", key: "LIKELY"};
    } else {
      var m = cOsaMarkers();
      osa = m.length >= 3 ? {lvl: "high", t: "High risk of sleep apnoea", key: "HIGH"} : m.length >= 1 ? {lvl: "mid", t: "Sleep apnoea possible", key: "MODERATE"} : {lvl: "low", t: "Sleep apnoea less likely"};
      osa.why = m.join(", ");
    }
    var comp = [{name: "Sleep apnoea", lvl: osa.lvl, t: osa.t, why: osa.why}];
    var gt = g.flags.length ? g.flags.join(", ") : (g.measured ? "within the normal range" : "no problems reported");
    if (!g.abnormal) gt = gt.charAt(0).toUpperCase() + gt.slice(1);
    comp.push({name: "Growth", lvl: g.thrive ? "high" : g.abnormal ? "mid" : "low", t: (g.thrive ? "Growth may be affected: " : g.abnormal ? "Weight needs attention: " : "") + gt, why: g.text});
    if (mod.ears || A.q18) {
      var aom = inSet(A.q18, "ab"), glue = (Array.isArray(A.q19) && A.q19.some(function (x) { return x !== "d"; })) || inSet(A.q23, "ab");
      comp.push({name: "Ear infections", lvl: aom ? "mid" : "low", t: aom ? "Recurrent ear infections" : "Not recurrent"});
      comp.push({name: "Hearing", lvl: glue ? "mid" : "low", t: glue ? "Possible fluid behind the eardrums (glue ear): a hearing test and ear check are advised" : "No hearing concerns"});
    } else comp.push({name: "Ears and hearing", lvl: "low", t: "No ear or hearing problems reported"});
    comp.push({name: "Throat and nose", lvl: A.q20 === "a" ? "mid" : A.q20 === "b" ? "mid" : "low",
      t: A.q20 === "a" ? "Frequent tonsillitis: an ENT review is advised" : A.q20 === "b" ? "Long-standing nasal blockage: adenoids or allergy may be the cause" : "No frequent infections reported"});
    var face = Array.isArray(A.q16) && A.q16.some(function (x) { return "bcd".indexOf(x) !== -1; });
    if (face) comp.push({name: "Face and teeth", lvl: "mid", t: "Changes in the face or teeth: an orthodontic assessment may help"});
    R.comp = comp;
    R.osaKey = osa.key;

    /* 3. Tonsils for age */
    var to;
    if (A.q24 === "a") to = {lvl: "high", t: "Large, as told by a doctor earlier (to be confirmed at examination)"};
    else if (A.q24 === "b") to = {lvl: "low", t: "Normal size, as told by a doctor earlier (to be confirmed at examination)"};
    else if (A.q17 === "a") to = {lvl: "high", t: "Very large (parent's impression, to be confirmed at examination)"};
    else if (A.q17 === "b") to = a < 8 ? {lvl: "mid", t: "Large, which is common at this age (parent's impression, to be confirmed at examination)"} : {lvl: "mid", t: "Large for age (parent's impression, to be confirmed at examination)"};
    else if (A.q17 === "c") to = {lvl: "low", t: "Appropriate for age (parent's impression, to be confirmed at examination)"};
    else to = {lvl: "low", t: "Not assessed"};
    R.tonsil = to;

    /* Action */
    var urgent = osa.key === "HIGH" || g.thrive;
    var check = osa.key === "LIKELY" || osa.key === "MODERATE" || comp.some(function (c) { return c.name !== "Sleep apnoea" && c.name !== "Growth" && c.lvl !== "low"; }) || ad.lvl !== "low" || to.lvl !== "low" || g.abnormal;
    if (urgent) R.action = {lvl: "high", t: "Please book an ENT consultation soon."};
    else if (check) R.action = {lvl: "mid", t: "An ENT check is advised."};
    else R.action = {lvl: "low", t: "No major warning signs were found in your answers. This check cannot rule out enlarged adenoids or tonsils. If your child snores, breathes through the mouth or has frequent colds or ear problems, please confirm with a consultation with an ENT doctor or paediatrician. An X-ray or nasal endoscopy may be advised."};
    return R;
  }

  /* =====================================================================
     ENGINE AND RENDERING
     ===================================================================== */
  var Q = TOOL === "child" ? CQ : AQ;
  var nextFn = TOOL === "child" ? childNext : adultNext;

  function stopMessage() {
    if (TOOL === "child" && A.age) {
      var a = cAge();
      if (a < 2) return "For a child under 2 who snores or breathes noisily, please see a doctor directly.";
      if (a >= 18) return 'From 18 years, please use the <a href="' + esc(box.getAttribute("data-adult-url") || "sleep-score.html") + '">adult check</a>.';
    }
    if (TOOL === "adult" && A.age && A.age.y < 18) return 'This check is for adults. For children and teenagers up to 17, please use the <a href="' + esc(box.getAttribute("data-child-url") || "child-sleep-score.html") + '">child check</a>.';
    return null;
  }
  function current() {
    if (extra) { for (var i = 0; i < extra.length; i++) if (A[extra[i]] == null) return extra[i]; return null; }
    if (stopMessage()) return "__stop";
    return nextFn();
  }
  function answer(id, v) {
    A[id] = v; path.push(id);
    show();
  }
  function back() {
    if (!path.length) return;
    if (extra && extra.indexOf(path[path.length - 1]) === -1) { extra = null; show(); return; }
    var id = path.pop(); delete A[id];
    if (TOOL === "adult" && !extra && adultNext()) frozen = null;
    show();
  }
  function restart() { A = {}; path = []; extra = null; frozen = null; show(); }

  function navRow(withNext) {
    var nav = el("div", "flow-nav");
    if (path.length) { var b = el("button", "btn quiet", "Back"); b.type = "button"; b.onclick = back; nav.appendChild(b); }
    if (withNext) { var n = el("button", "btn", "Continue"); n.type = "submit"; nav.appendChild(n); }
    return nav;
  }

  function renderQuestion(id) {
    var q = Q[id], card = el("form", "flow-card");
    card.setAttribute("novalidate", "");
    card.appendChild(el("p", "flow-step", "Question " + (path.length + 1)));
    var h = el("h2", "flow-q"); h.textContent = q.q; h.tabIndex = -1; card.appendChild(h);
    if (q.hint) card.appendChild(el("p", "q-hint", esc(q.hint)));
    if (q.fig) card.insertAdjacentHTML("beforeend", tonsilFigure());
    var err = el("p", "score-missing"); err.hidden = true;

    if (!q.type) {
      var opts = el("div", "opts");
      q.opts.forEach(function (t, i) {
        if (q.from && i < q.from) return;
        var b = el("button", "opt opt-btn"); b.type = "button"; b.textContent = t;
        b.onclick = function () { answer(id, L[i]); };
        opts.appendChild(b);
      });
      card.appendChild(opts);
      card.appendChild(navRow(false));
    } else if (q.type === "multi") {
      var mo = el("div", "opts");
      q.opts.forEach(function (t, i) {
        var lab = el("label", "opt"), cb = el("input"); cb.type = "checkbox"; cb.value = L[i];
        cb.onchange = function () {
          if (!cb.checked) return;
          if (L[i] === q.none) mo.querySelectorAll("input").forEach(function (x) { if (x !== cb) x.checked = false; });
          else { var n = mo.querySelector('input[value="' + q.none + '"]'); if (n) n.checked = false; }
        };
        lab.appendChild(cb); lab.appendChild(el("span", null, esc(t))); mo.appendChild(lab);
      });
      card.appendChild(mo); card.appendChild(err); card.appendChild(navRow(true));
      card.onsubmit = function (e) {
        e.preventDefault();
        var v = Array.prototype.map.call(mo.querySelectorAll("input:checked"), function (x) { return x.value; });
        if (!v.length) { err.textContent = "Please tick at least one, or \"" + q.opts[L.indexOf(q.none)] + "\"."; err.hidden = false; return; }
        answer(id, v);
      };
    } else if (q.type === "number" || q.type === "bmi") {
      var fields = q.type === "bmi" ? [{id: "cm", label: "Height (cm)", min: 120, max: 230}, {id: "kg", label: "Weight (kg)", min: 25, max: 300}] : q.fields;
      var row = el("div", "bmi-row"), ins = {};
      fields.forEach(function (f) {
        var lab = el("label", null, esc(f.label)), inp = el("input");
        inp.type = "number"; inp.inputMode = f.id === "y" || f.id === "m" ? "numeric" : "decimal"; inp.min = f.min; inp.max = f.max;
        if (f.optional) inp.placeholder = "0";
        lab.appendChild(inp); row.appendChild(lab); ins[f.id] = inp;
      });
      card.appendChild(row); card.appendChild(err);
      var nav = navRow(true);
      if (q.skip) { var sk = el("button", "btn quiet", esc(q.skip)); sk.type = "button"; sk.onclick = function () { answer(id, {}); }; nav.appendChild(sk); }
      card.appendChild(nav);
      if (q.type === "bmi") {
        card.appendChild(el("p", "q-hint flow-or", "Or, if you don't know your height and weight:"));
        var bo = el("div", "opts");
        q.opts.forEach(function (t, i) {
          var b = el("button", "opt opt-btn"); b.type = "button"; b.textContent = t;
          b.onclick = function () { answer(id, {v: L[i], text: t}); };
          bo.appendChild(b);
        });
        card.appendChild(bo);
      }
      card.onsubmit = function (e) {
        e.preventDefault();
        var v = {}, bad = [];
        fields.forEach(function (f) {
          var raw = ins[f.id].value.trim(), n = parseFloat(raw);
          if (raw === "" && f.optional) { v[f.id] = 0; return; }
          if (raw === "" && q.skip) return;
          if (isNaN(n) || n < f.min || n > f.max) bad.push(f.label + " (" + f.min + " to " + f.max + ")");
          else v[f.id] = n;
        });
        if (q.type === "bmi" && (!v.cm || !v.kg)) bad = bad.length ? bad : ["height and weight, or choose a description below"];
        if (q.skip && !v.cm && !bad.length) bad.push("the height, or choose \"" + q.skip + "\"");
        if (bad.length) { err.textContent = "Please enter " + bad.join(" and ") + "."; err.hidden = false; return; }
        if (q.type === "bmi") v.bmi = Math.round(v.kg / Math.pow(v.cm / 100, 2) * 10) / 10;
        answer(id, v);
      };
    }
    return card;
  }

  function answerText(id) {
    var q = Q[id], v = A[id];
    if (id === "age") return TOOL === "child" ? v.y + " years" + (v.m ? " " + v.m + " months" : "") : v.y + " years";
    if (id === "hw") return v.cm ? v.cm + " cm" + (v.kg ? ", " + v.kg + " kg" : "") : "Not known";
    if (q.type === "bmi") return v.bmi ? v.cm + " cm, " + v.kg + " kg (BMI " + v.bmi + ")" : v.text;
    if (Array.isArray(v)) return v.map(function (x) { return q.opts[L.indexOf(x)]; }).join("; ");
    return q.opts[L.indexOf(v)];
  }
  function summary() {
    var wrap = el("details", "flow-answers");
    wrap.appendChild(el("summary", null, "Your answers (" + path.length + ")"));
    var ol = el("ul");
    var ids = path.slice();
    if (TOOL === "adult") ids.sort(function (x, y) { return A_ORDER.indexOf(x) - A_ORDER.indexOf(y); });
    ids.forEach(function (id) { ol.appendChild(el("li", null, "<strong>" + esc(Q[id].label) + ":</strong> " + esc(answerText(id)))); });
    wrap.appendChild(ol);
    return wrap;
  }
  function waText(result) {
    var name = TOOL === "child" ? "MERA Child Sleep Apnoea Check" : "MERA Sleep Apnoea Check";
    return "Hello, I did the " + name + " on entmidas.com.\nResult: " + result + "\nI would like to book a consultation.";
  }
  function contact(card, result) {
    var tel = box.getAttribute("data-tel");
    if (!tel) { card.appendChild(el("p", null, "Take a screenshot of this result and show it to your doctor.")); return; }
    card.appendChild(el("p", null, "Send your result on WhatsApp to book, or take a screenshot and show it at your consultation."));
    var p = el("p", "intro-actions");
    p.innerHTML = '<a class="btn" href="' + esc(box.getAttribute("data-wa")) + "?text=" + encodeURIComponent(waText(result)) + '">Send my result on WhatsApp</a> <a class="btn quiet" href="tel:' + esc(tel) + '">Call ' + esc(box.getAttribute("data-tel-show")) + '</a>';
    card.appendChild(p);
  }
  function tail(card) {
    var nav = el("div", "flow-nav");
    var b = el("button", "btn quiet", "Back"); b.type = "button"; b.onclick = back; nav.appendChild(b);
    var r = el("button", "btn quiet", "Start again"); r.type = "button"; r.onclick = restart; nav.appendChild(r);
    card.appendChild(nav);
  }

  function renderAdultResult() {
    var r = frozen || adultResult(), card = el("section", "score-result flow-result");
    card.setAttribute("aria-live", "polite");
    card.appendChild(el("h2", null, "Your result"));
    if (r.urgent) card.appendChild(el("div", "urgent", "<strong>" + esc(r.urgent) + "</strong>"));
    card.appendChild(el("p", "score-band " + r.level, esc(r.title)));
    card.appendChild(el("p", null, esc(r.text)));
    r.adds.forEach(function (t) { card.appendChild(el("p", "flow-add", esc(t))); });
    if (r.why) card.appendChild(el("p", "q-hint", "Based on: " + esc(r.why) + "."));
    card.appendChild(el("p", "q-hint", "This is a self-check, not a diagnosis. Only a sleep study can confirm sleep apnoea."));
    var left = A_ORDER.filter(function (k) { return A[k] == null; });
    if (left.length && !extra) {
      var more = el("button", "btn quiet", "Answer " + left.length + " more question" + (left.length > 1 ? "s" : "") + " for your doctor (optional)");
      more.type = "button";
      more.onclick = function () { frozen = r; extra = left; show(); };
      card.appendChild(el("p")).appendChild(more);
    }
    card.appendChild(summary());
    contact(card, r.title); tail(card);
    return card;
  }
  function row(name, x) {
    var li = el("li", "rc-row");
    li.appendChild(el("span", "rc-name", esc(name)));
    var v = el("span", "rc-val " + x.lvl, esc(x.t)); li.appendChild(v);
    if (x.why) li.appendChild(el("span", "rc-why", esc(x.why)));
    return li;
  }
  function renderChildResult() {
    var R = childResult(), card = el("section", "score-result flow-result");
    card.setAttribute("aria-live", "polite");
    card.appendChild(el("h2", null, "Your child's report"));
    card.appendChild(el("div", "urgent", "<strong>Seek urgent medical care</strong> if your child has long pauses in breathing, turns blue or pale during sleep, or is struggling hard to breathe."));
    card.appendChild(el("p", "score-band " + R.action.lvl, esc(R.action.t)));
    card.appendChild(el("h3", null, "1. Adenoids"));
    var u1 = el("ul", "rc"); u1.appendChild(row("Adenoids", {lvl: R.adenoid.lvl, t: R.adenoid.t, why: R.adenoid.doc}));
    card.appendChild(u1);
    if (R.adenoid.note) card.appendChild(el("p", "flow-add", esc(R.adenoid.note)));
    card.appendChild(el("h3", null, "2. Complications"));
    var u2 = el("ul", "rc"); R.comp.forEach(function (c) { u2.appendChild(row(c.name, c)); }); card.appendChild(u2);
    card.appendChild(el("h3", null, "3. Tonsil size for age"));
    var u3 = el("ul", "rc"); u3.appendChild(row("Tonsils", R.tonsil)); card.appendChild(u3);
    card.appendChild(el("p", "q-hint", "This is a check, not a diagnosis. Every child has adenoids; the question is whether they are enlarged enough to cause problems."));
    card.appendChild(summary());
    contact(card, R.action.t.split(". ")[0].replace(/\.$/, "")); tail(card);
    return card;
  }

  var sent = false; /* analytics: records only that a check was completed, never answers or result */
  function show() {
    box.innerHTML = "";
    var id = current(), node;
    if (id === "__stop") {
      node = el("div", "flow-card");
      node.appendChild(el("p", "score-band mid", stopMessage()));
      node.appendChild(navRow(false));
    } else if (id) node = renderQuestion(id);
    else if (extra) { extra = null; node = renderAdultResult(); }
    else node = TOOL === "child" ? renderChildResult() : renderAdultResult();
    if (!id && !sent && window.gtag) { sent = true; gtag("event", "check_complete", {check_name: "mera_" + TOOL}); }
    box.appendChild(node);
    var f = node.querySelector(".flow-q, h2");
    if (f && path.length) { f.tabIndex = -1; f.focus({preventScroll: true}); box.scrollIntoView({behavior: "smooth", block: "start"}); }
  }

  /* test hook: lets automated checks read the decision logic */
  window.MERA_FLOW = {answers: function () { return A; }, next: function () { return current(); },
    result: function () { return TOOL === "child" ? childResult() : (frozen || adultResult()); }};
  show();
})();
