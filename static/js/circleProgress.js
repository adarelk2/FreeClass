// circleProgress.js
class CircleProgress {
    constructor(container, {
        size = 120,
        stroke = 10,
        value = 0,
        color = "#22c55e",
        background = "#e5e7eb",
        textColor = "#fff",
        fontSize = 20
    } = {}) {

        this.size = size;
        this.stroke = stroke;
        this.radius = (size - stroke) / 2;
        this.circumference = 2 * Math.PI * this.radius;

        this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        this.svg.setAttribute("width", size);
        this.svg.setAttribute("height", size);

        // Background circle
        const bg = this.createCircle(background);

        // Progress circle
        this.progress = this.createCircle(color);
        this.progress.style.strokeDasharray = this.circumference;
        this.progress.style.strokeDashoffset = this.circumference;
        this.progress.style.transition = "stroke-dashoffset 0.6s ease";

        // Text
        this.text = document.createElement("div");
        this.text.style.position = "absolute";
        this.text.style.inset = "0";
        this.text.style.display = "flex";
        this.text.style.alignItems = "center";
        this.text.style.justifyContent = "center";
        this.text.style.fontSize = fontSize + "px";
        this.text.style.fontWeight = "600";
        this.text.style.color = textColor;

        const wrapper = document.createElement("div");
        wrapper.style.position = "relative";
        wrapper.style.width = size + "px";
        wrapper.style.height = size + "px";

        this.svg.append(bg, this.progress);
        wrapper.append(this.svg, this.text);
        container.append(wrapper);

        this.set(value);
    }

    createCircle(color) {
        const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        c.setAttribute("cx", this.size / 2);
        c.setAttribute("cy", this.size / 2);
        c.setAttribute("r", this.radius);
        c.setAttribute("fill", "none");
        c.setAttribute("stroke", color);
        c.setAttribute("stroke-width", this.stroke);
        c.setAttribute("transform", `rotate(-90 ${this.size / 2} ${this.size / 2})`);
        return c;
    }

    set(value) {
        value = Math.min(100, Math.max(0, value));
        const offset = this.circumference * (1 - value / 100);
        this.progress.style.strokeDashoffset = offset;
        this.text.innerText = value + "%";
    }
}
