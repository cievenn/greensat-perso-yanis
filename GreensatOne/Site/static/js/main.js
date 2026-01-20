/* =========================================
   MAIN.JS - AVEC THEME MANAGER & PERF V3
   ========================================= */

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

/* --- 1. CORE SYSTEM & CURSOR --- */
const cursorOuter = document.getElementById("cursor-outer");
const cursorInner = document.getElementById("cursor-inner");
let mouseX = 0, mouseY = 0;
let cursorX = 0, cursorY = 0;

if (cursorOuter && cursorInner) {
    document.addEventListener("mousemove", (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        cursorInner.style.transform = `translate(${mouseX}px, ${mouseY}px)`;
        document.body.style.setProperty('--cursor-x', `${mouseX}px`);
        document.body.style.setProperty('--cursor-y', `${mouseY}px`);
    }, { passive: true });

    function animateCursor() {
        const dt = 0.15;
        cursorX += (mouseX - cursorX) * dt;
        cursorY += (mouseY - cursorY) * dt;
        cursorOuter.style.transform = `translate(${cursorX - 20}px, ${cursorY - 20}px)`;
        requestAnimationFrame(animateCursor);
    }
    animateCursor();
}

/* --- 2. AUDIO MANAGER --- */
class AudioManager {
    constructor() { this.ctx = null; this.enabled = false; }
    init() {
        if (!this.ctx) { this.ctx = new (window.AudioContext || window.webkitAudioContext)(); }
        this.enabled = true;
        const btn = document.getElementById('audio-toggle');
        if(btn) btn.innerText = "[ AUDIO: ON ]";
        this.playBeep(600, 'sine', 0.05);
    }
    toggle() {
        if (this.enabled) { 
            this.enabled = false; 
            const btn = document.getElementById('audio-toggle');
            if(btn) btn.innerText = "[ AUDIO: OFF ]"; 
        } else { this.init(); }
    }
    playBeep(freq = 400, type = 'sine', duration = 0.1) {
        if (!this.enabled || !this.ctx) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = typeof type === 'string' ? type : 'sine';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.05, this.ctx.currentTime); 
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + duration);
    }
    playAlert() {
        if (!this.enabled) return;
        this.playBeep(150, 'sawtooth', 0.3);
        setTimeout(() => this.playBeep(100, 'sawtooth', 0.3), 150);
    }
}
const sfx = new AudioManager();
const audioBtn = document.getElementById('audio-toggle');
if(audioBtn) audioBtn.addEventListener('click', () => sfx.toggle());

document.querySelectorAll('button, .chart-tab, .hover-sfx').forEach(el => {
    el.addEventListener('mouseenter', () => {
        if(cursorOuter) {
            cursorOuter.style.borderColor = 'var(--c-accent-secondary)';
            cursorOuter.style.transform += ' scale(1.5)';
        }
        sfx.playBeep(800, 'sine', 0.05);
    });
    el.addEventListener('mouseleave', () => {
        if(cursorOuter) {
            cursorOuter.style.borderColor = 'rgba(255,255,255,0.3)';
            cursorOuter.style.transform = cursorOuter.style.transform.replace(' scale(1.5)', '');
        }
    });
    el.addEventListener('click', () => sfx.playBeep(1200, 'square', 0.1));
});

/* --- 3. THEME MANAGER (NOUVEAU) --- */
const themeBtn = document.getElementById('theme-toggle');
let isLightMode = localStorage.getItem('theme') === 'light';

// Appliquer le thème au chargement
if (isLightMode) {
    document.body.classList.add('light-mode');
    if(themeBtn) themeBtn.innerText = "[ MODE: LIGHT ]";
}

if(themeBtn) {
    themeBtn.addEventListener('click', () => {
        isLightMode = !isLightMode;
        document.body.classList.toggle('light-mode', isLightMode);
        themeBtn.innerText = isLightMode ? "[ MODE: LIGHT ]" : "[ MODE: DARK ]";
        
        // Sauvegarde
        localStorage.setItem('theme', isLightMode ? 'light' : 'dark');
        
        // Mise à jour du graphique (couleurs des grilles)
        updateChartTheme();
        
        sfx.playBeep(600, 'sine', 0.1);
    });
}

function updateChartTheme() {
    if (!mainChart) return;
    
    const gridColor = isLightMode ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.05)';
    const textColor = isLightMode ? 'rgba(0,0,0,0.5)' : 'rgba(255,255,255,0.5)';
    
    mainChart.options.scales.y.grid.color = gridColor;
    Chart.defaults.color = textColor;
    mainChart.update('none'); // Update sans animation
}

/* --- 4. TILT 3D --- */
let isTilting = false;
document.querySelectorAll('.tilt-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        if(isTilting) return;
        isTilting = true;
        requestAnimationFrame(() => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -3; 
            const rotateY = ((x - centerX) / centerX) * 3;
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.01)`;
            isTilting = false;
        });
    });
    card.addEventListener('mouseleave', () => {
        card.style.transform = `perspective(1000px) rotateX(0) rotateY(0) scale(1)`;
    });
});

/* --- 5. 3D BACKGROUND --- */
function init3DScene() {
    const canvas = document.querySelector('#scene-3d');
    if (!canvas) return;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.z = 5; camera.position.x = 2;
    
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true, powerPreference: "high-performance" });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));

    scene.add(new THREE.AmbientLight(0x404040, 2));
    const dirLight = new THREE.DirectionalLight(0x2e5cff, 3);
    dirLight.position.set(5, 5, 5); scene.add(dirLight);
    const rimLight = new THREE.PointLight(0x00e5ff, 5);
    rimLight.position.set(-5, 0, -5); scene.add(rimLight);
    
    let model;
    new GLTFLoader().load('/static/models/satellite.glb', (gltf) => {
        model = gltf.scene;
        model.scale.set(1.5, 1.5, 1.5);
        new THREE.Box3().setFromObject(model).getCenter(model.position).multiplyScalar(-1);
        scene.add(model);
    });

    function animate() {
        requestAnimationFrame(animate);
        if (model) {
            model.rotation.y += 0.002;
            model.rotation.x = Math.sin(Date.now() * 0.0005) * 0.1;
            model.position.y = Math.sin(Date.now() * 0.001) * 0.2;
        }
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

/* --- 6. ORB --- */
const orbCanvas = document.getElementById('orb-canvas');
let orbState = 'normal';
function initOrb() {
    if (!orbCanvas) return;
    const oCtx = orbCanvas.getContext('2d', { alpha: true });
    let orbW = 0, orbH = 0; let time = 0;
    
    function resizeOrb() {
        const rect = orbCanvas.parentElement.getBoundingClientRect();
        if(rect.width === 0) return;
        orbW = orbCanvas.width = rect.width; 
        orbH = orbCanvas.height = rect.height;
    }
    window.addEventListener('resize', resizeOrb);
    setTimeout(resizeOrb, 0);

    function drawOrb() {
        requestAnimationFrame(drawOrb);
        if (!orbW || !orbH) return; 
        oCtx.clearRect(0, 0, orbW, orbH);
        const cx = orbW / 2; const cy = orbH / 2;
        time += 0.01;
        
        let baseR = 60 + Math.sin(time * 2) * 5;
        let colorStops = ['#2e5cff', '#00f2ff']; 
        if (orbState === 'warning') colorStops = ['#ffb800', '#ffeb3b'];
        if (orbState === 'danger') { colorStops = ['#ff2e5c', '#ff1744']; baseR = 60 + Math.sin(time * 15) * 10; }
        
        oCtx.lineWidth = 2; oCtx.strokeStyle = colorStops[0];
        
        const g = oCtx.createRadialGradient(cx, cy, 0, cx, cy, baseR);
        g.addColorStop(0, colorStops[1]); g.addColorStop(0.7, colorStops[0]); g.addColorStop(1, 'transparent');
        oCtx.fillStyle = g; oCtx.globalAlpha = 0.5;
        oCtx.beginPath(); oCtx.arc(cx, cy, baseR, 0, Math.PI * 2); oCtx.fill();
        
        for (let i = 0; i < 2; i++) {
            oCtx.beginPath();
            oCtx.globalAlpha = 1 - (i * 0.4);
            for (let a = 0; a < Math.PI * 2; a += 0.2) {
                let r = baseR + (i * 15) + Math.sin(a * 5 + time * (i+1)) * 5;
                const x = cx + Math.cos(a) * r; const y = cy + Math.sin(a) * r;
                if (a === 0) oCtx.moveTo(x, y); else oCtx.lineTo(x, y);
            }
            oCtx.closePath(); oCtx.stroke();
        }
    }
    drawOrb();
}

/* =========================================================================
   7. DATA & SMART NAVIGATION
   ========================================================================= */

let mainChart;
let currentChartMode = 'thermal';
let viewMode = 'day'; 
let currentReferenceDate = new Date(); 
let databaseMinDate = null; 

async function initLimits() {
    try {
        const res = await fetch('/api/limits');
        const data = await res.json();
        if (data.first_date) databaseMinDate = new Date(data.first_date);
    } catch(e) {}
}

function formatDateTimeISO(d) { return d.toISOString().replace('T', ' ').split('.')[0]; }

function getDateRange() {
    let start = new Date(currentReferenceDate);
    let end = new Date(currentReferenceDate);
    
    if (viewMode === 'day') {
        start.setHours(0,0,0,0); end.setHours(23,59,59);
        const now = new Date();
        let label = `${start.getDate()}/${start.getMonth()+1}/${start.getFullYear()}`;
        if (start.toDateString() === now.toDateString()) label = "LIVE TODAY";
        return { start: formatDateTimeISO(start), end: formatDateTimeISO(end), label: label };
    }
    else if (viewMode === 'week') {
        const day = start.getDay() || 7; 
        if (day !== 1) start.setHours(-24 * (day - 1)); else start.setHours(0,0,0,0);
        end = new Date(start); end.setDate(start.getDate() + 6); end.setHours(23,59,59);
        const label = `${start.getDate()}/${start.getMonth()+1} - ${end.getDate()}/${end.getMonth()+1}`;
        return { start: formatDateTimeISO(start), end: formatDateTimeISO(end), label: label };
    }
    else if (viewMode === 'month') {
        start.setDate(1); start.setHours(0,0,0,0);
        end = new Date(start); end.setMonth(start.getMonth() + 1); end.setDate(0); end.setHours(23,59,59);
        const label = start.toLocaleString('en-US', { month: 'long', year: 'numeric' }).toUpperCase();
        return { start: formatDateTimeISO(start), end: formatDateTimeISO(end), label: label };
    }
    else if (viewMode === 'year') {
        start.setMonth(0, 1); start.setHours(0,0,0,0);
        end = new Date(start); end.setFullYear(start.getFullYear() + 1); end.setDate(0); end.setHours(23,59,59);
        return { start: formatDateTimeISO(start), end: formatDateTimeISO(end), label: start.getFullYear() };
    }
}

window.changeDate = function(direction) {
    if (viewMode === 'day') currentReferenceDate.setDate(currentReferenceDate.getDate() + direction);
    else if (viewMode === 'week') currentReferenceDate.setDate(currentReferenceDate.getDate() + (direction * 7));
    else if (viewMode === 'month') currentReferenceDate.setMonth(currentReferenceDate.getMonth() + direction);
    else if (viewMode === 'year') currentReferenceDate.setFullYear(currentReferenceDate.getFullYear() + direction);
    
    updateNavUI();
    loadHistoryData();
    sfx.playBeep(1000, 'square', 0.05);
}

window.switchTimeRange = function(range) {
    viewMode = range;
    currentReferenceDate = new Date(); 
    document.querySelectorAll('.time-tab').forEach(b => b.classList.remove('active'));
    if(event && event.target) event.target.classList.add('active');
    const navControls = document.getElementById('chart-nav-controls');
    if (navControls) navControls.style.display = 'flex'; 
    updateNavUI();
    loadHistoryData();
    sfx.playBeep(800, 'sine', 0.1);
}

function updateNavUI() {
    const rangeData = getDateRange();
    document.getElementById('nav-label').innerText = rangeData.label;
    const prevBtn = document.querySelector('.nav-btn:first-child'); 
    const nextBtn = document.getElementById('nav-next');
    const now = new Date();
    
    if (new Date(rangeData.end) >= now) { nextBtn.classList.add('disabled'); nextBtn.style.opacity = '0'; nextBtn.style.pointerEvents = 'none'; } 
    else { nextBtn.classList.remove('disabled'); nextBtn.style.opacity = '1'; nextBtn.style.pointerEvents = 'auto'; }

    if (databaseMinDate && new Date(rangeData.start) <= databaseMinDate) { prevBtn.classList.add('disabled'); prevBtn.style.opacity = '0'; prevBtn.style.pointerEvents = 'none'; } 
    else { prevBtn.classList.remove('disabled'); prevBtn.style.opacity = '1'; prevBtn.style.pointerEvents = 'auto'; }
}

window.switchChart = function(mode) {
    currentChartMode = mode;
    const typeTabs = document.querySelectorAll('.chart-tab:not(.time-tab)');
    typeTabs.forEach(b => b.classList.remove('active'));
    if(event && event.target) event.target.classList.add('active');
    updateChartData(); 
    sfx.playBeep(800, 'sine', 0.1);
}

let chartHistory = { labels: [], temp: [], hum: [], gas: [], press: [], lux: [] };

async function loadHistoryData() {
    const range = getDateRange();
    const url = `/api/history?start=${range.start}&end=${range.end}&mode=${viewMode}`;

    try {
        const response = await fetch(url);
        if (!response.ok) return;
        const data = await response.json();
        
        chartHistory = { labels: [], temp: [], hum: [], gas: [], press: [], lux: [] };
        
        data.forEach(d => {
            let label = "";
            const dateObj = new Date(d.date_time);
            if (viewMode === 'day') label = d.date_time.split(' ')[1].substring(0, 5); 
            else if (viewMode === 'week') label = `${dateObj.getDate()}/${dateObj.getMonth()+1} ${dateObj.getHours()}h`;
            else if (viewMode === 'month') label = `${dateObj.getDate()}/${dateObj.getMonth()+1}`;
            else if (viewMode === 'year') label = `${dateObj.getMonth()+1}/${dateObj.getFullYear()}`;

            chartHistory.labels.push(label);
            chartHistory.temp.push(d.temp);
            chartHistory.hum.push(d.hum);
            chartHistory.gas.push(d.gaz_pct);
            chartHistory.press.push(d.press);
            chartHistory.lux.push(d.lux);
        });
        
        updateChartData();
        
    } catch(e) { console.error("History Error", e); }
}

function updateChartData() {
    if(!mainChart) return;
    mainChart.options.animation = false;
    mainChart.data.labels = chartHistory.labels;
    mainChart.data.datasets = [];
    
    const grad = (c) => {
        const ctx = document.getElementById('mainChart').getContext('2d');
        const g = ctx.createLinearGradient(0, 0, 0, 300);
        g.addColorStop(0, c + '66'); g.addColorStop(1, c + '00');
        return g;
    };

    const commonOpts = { fill: true, tension: 0.3, pointRadius: 0, pointHitRadius: 10, borderWidth: 2 };

    if(currentChartMode === 'thermal') {
        mainChart.data.datasets.push(
            { label: 'TEMP', data: chartHistory.temp, borderColor: '#ff2e5c', backgroundColor: grad('#ff2e5c'), ...commonOpts },
            { label: 'HUM', data: chartHistory.hum, borderColor: '#2e5cff', backgroundColor: grad('#2e5cff'), ...commonOpts }
        );
    } else if (currentChartMode === 'air') {
        mainChart.data.datasets.push(
            { label: 'GAS', data: chartHistory.gas, borderColor: '#00ffa3', backgroundColor: grad('#00ffa3'), ...commonOpts },
            { label: 'PRES', data: chartHistory.press, borderColor: '#b0b0b0', borderDash: [5,5], fill: false, ...commonOpts, yAxisID: 'y1' }
        );
    } else if (currentChartMode === 'light') {
         mainChart.data.datasets.push(
            { label: 'LUX', data: chartHistory.lux, borderColor: '#ffb800', backgroundColor: grad('#ffb800'), ...commonOpts }
        );
    }
    mainChart.update();
}

if(document.getElementById('mainChart')) {
    const chartCtx = document.getElementById('mainChart').getContext('2d');
    // On met la couleur de base selon le thème
    const isLight = document.body.classList.contains('light-mode');
    Chart.defaults.font.family = "'JetBrains Mono', monospace";
    Chart.defaults.color = isLight ? "rgba(0,0,0,0.5)" : "rgba(255,255,255,0.5)";

    mainChart = new Chart(chartCtx, {
        type: 'line',
        data: { labels: [], datasets: [] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, 
            normalized: true, 
            spanGaps: true, 
            interaction: { mode: 'nearest', axis: 'x', intersect: false },
            plugins: { legend: { display: false }, tooltip: { enabled: true, animation: false } },
            scales: {
                x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
                y: { grid: { color: isLight ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.05)' } },
                y1: { display: false, position: 'right' }
            }
        }
    });
    window.switchChart('thermal');
}

async function fetchData() {
    try {
        const response = await fetch('/api/data');
        if (!response.ok) throw new Error("API Offline");
        const data = await response.json();

        updateText('val-temp', data.temp, '°C');
        updateText('val-hum', data.hum, '%');
        updateText('val-gas', data.gaz_pct, '%');
        updateText('val-lux', data.lux, 'Lx');
        updateText('val-pres', data.press, '');
        let aqi = data.air_pct || Math.round(data.gaz_pct * 1.5);
        updateText('aqi-score', aqi, '');
        updateBar('bar-temp', data.temp, 50);
        updateBar('bar-hum', data.hum, 100);
        updateBar('bar-gas', data.gaz_pct, 100);
        updateBar('bar-lux', data.lux, 1000); 

        const statusText = document.getElementById('main-status-text');
        const globalDot = document.getElementById('global-status-dot');
        const connStatus = document.getElementById('connection-status');
        const cardGas = document.getElementById('card-gas');
        const cardOrb = document.getElementById('card-orb');
        
        if (connStatus) { connStatus.innerText = "CONNECTED"; connStatus.style.color = "var(--c-accent-success)"; }

        if (data.gaz_pct > 20) {
            orbState = 'danger';
            if(statusText) { statusText.innerText = "CRITICAL"; statusText.style.background = "var(--c-accent-danger)"; }
            if(globalDot) globalDot.style.background = "var(--c-accent-danger)";
            if(cardOrb) cardOrb.classList.add('alert-critical');
            sfx.playAlert(); 
        } else {
            orbState = 'normal';
            if(statusText) { statusText.innerText = "NOMINAL"; statusText.style.background = "rgba(255,255,255,0.1)"; }
            if(globalDot) globalDot.style.background = "var(--c-accent-success)";
            if(cardOrb) cardOrb.classList.remove('alert-critical');
        }

        const isToday = new Date().toDateString() === currentReferenceDate.toDateString();
        if (viewMode === 'day' && isToday) {
            const timeLabel = data.date_time.split(' ')[1].substring(0, 5);
            if (chartHistory.labels[chartHistory.labels.length - 1] !== timeLabel) {
                chartHistory.labels.push(timeLabel);
                chartHistory.temp.push(data.temp);
                chartHistory.hum.push(data.hum);
                chartHistory.gas.push(data.gaz_pct);
                chartHistory.press.push(data.press);
                chartHistory.lux.push(data.lux);
                
                if (chartHistory.labels.length > 200) { 
                    chartHistory.labels.shift();
                    chartHistory.temp.shift(); chartHistory.hum.shift();
                    chartHistory.gas.shift(); chartHistory.press.shift(); chartHistory.lux.shift();
                }
                updateChartData();
            }
        }

    } catch (e) {
        const connStatus = document.getElementById('connection-status');
        if (connStatus) { connStatus.innerText = "OFFLINE"; connStatus.style.color = "var(--c-accent-danger)"; }
    }
}

function updateText(id, val, unit) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = `${val}<span class="text-sm opacity-50 ml-1 font-normal">${unit}</span>`;
}
function updateBar(id, val, max) {
    const el = document.getElementById(id);
    if (el) {
        const pct = Math.min((val / max) * 100, 100);
        el.style.width = `${pct}%`;
    }
}
setInterval(() => {
    const now = new Date();
    const clock = document.getElementById('clock-display');
    const date = document.getElementById('date-display');
    if(clock) clock.innerText = now.toLocaleTimeString('fr-FR');
    if(date) date.innerText = now.toISOString().split('T')[0];
}, 1000);

window.addEventListener('load', () => {
    initOrb();
    init3DScene();
    initLimits().then(() => {
        switchTimeRange('day');
    });
    
    if(typeof gsap !== 'undefined') {
        const tl = gsap.timeline();
        tl.to("#preloader", { opacity: 0, duration: 0.5, onComplete: () => { const pl = document.getElementById('preloader'); if(pl) pl.remove(); }})
        .from("header", { y: -50, opacity: 0, duration: 1, ease: "power3.out" })
        .from(".glass", { y: 50, opacity: 0, duration: 0.8, stagger: 0.1, ease: "back.out(1.2)" }, "-=0.6");
    }
    
    setInterval(fetchData, 2000);
    console.log("System online.");
});