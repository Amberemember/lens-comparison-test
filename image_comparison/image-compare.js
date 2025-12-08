; (function (global) {
    class SynchronizedImageCompare {
        constructor(root, groups) {
            this.root = root;
            this.groups = groups || [];
            this.currentGroupIndex = 0;

            this.panes = Array.from(root.querySelectorAll(".compare-pane"));
            this.images = this.panes.map((p) => p.querySelector("img"));
            this.loadingOverlays = this.panes.map((p) =>
                p.querySelector(".compare-loading")
            );
            this.groupSelect = root.querySelector(".compare-select");
            this.statusEl = root.querySelector(".view-status");

            this.state = {
                scale: 1,
                offsetX: 0,
                offsetY: 0,
            };

            this.dragging = {
                active: false,
                startX: 0,
                startY: 0,
                originX: 0,
                originY: 0,
            };

            this.touchState = {
                mode: null,
                startX: 0,
                startY: 0,
                originX: 0,
                originY: 0,
                startDist: 0,
                startScale: 1,
            };

            this.MIN_SCALE = 1;
            this.MAX_SCALE = 8;
            this.DEFAULT_SCALE = 1;

            this.buildGroupSelect();
            if (this.groups.length > 0) {
                this.setGroup(0);
            }
            this.attachInteractions();
            this.updateStatus();

            global.addEventListener("resize", () => {
                this.clampOffsets();
                this.applyTransform();
            });
        }

        buildGroupSelect() {
            if (!this.groupSelect) return;

            if (!this.groups || this.groups.length <= 1) {
                const groupWrapper = this.groupSelect.closest('.compare-groups');
                if (groupWrapper) {
                    groupWrapper.style.display = 'none';
                }
                return; // 不再生成选项
            }

            this.groupSelect.innerHTML = "";
            this.groups.forEach((g, idx) => {
                const opt = document.createElement("option");
                opt.value = idx;
                opt.textContent = g.label || `组 ${idx + 1}`; // 防止没写 label
                this.groupSelect.appendChild(opt);
            });

            this.groupSelect.addEventListener("change", (e) => {
                const idx = Number(e.target.value);
                this.setGroup(idx);
            });
        }


        showLoading() {
            this.loadingOverlays.forEach((o) => o && o.classList.add("visible"));
        }

        hideLoading() {
            this.loadingOverlays.forEach((o) => o && o.classList.remove("visible"));
        }

        setGroup(index) {
            if (!this.groups[index]) return;
            this.currentGroupIndex = index;
            const group = this.groups[index];

            this.showLoading();

            this.state.scale = this.DEFAULT_SCALE;
            this.state.offsetX = 0;
            this.state.offsetY = 0;
            this.clampOffsets();
            this.applyTransform();
            this.updateStatus();

            if (this.groupSelect && this.groups.length > 1) {
                this.groupSelect.value = String(index);
            }

            let pending = this.images.length;
            const done = () => {
                pending--;
                if (pending <= 0) {
                    this.hideLoading();
                }
            };

            this.images.forEach((img, i) => {
                if (!img) return;

                img.onload = null;
                img.onerror = null;

                img.onload = () => done();
                img.onerror = () => done();

                const src = i === 0 ? group.left : group.right;
                img.src = src;

                if (img.complete && img.naturalWidth > 0) {
                    done();
                }
            });
        }

        attachInteractions() {
            this.panes.forEach((pane) => {
                pane.addEventListener(
                    "wheel",
                    (e) => this.onWheel(e),
                    { passive: false }
                );

                pane.addEventListener("mousedown", (e) => this.onDragStart(e));
                global.addEventListener("mousemove", (e) => this.onDragMove(e));
                global.addEventListener("mouseup", () => this.onDragEnd());
                pane.addEventListener("mouseleave", () => this.onDragEnd());

                pane.addEventListener(
                    "touchstart",
                    (e) => this.onTouchStart(e),
                    { passive: false }
                );
            });

            global.addEventListener(
                "touchmove",
                (e) => this.onTouchMove(e),
                { passive: false }
            );
            global.addEventListener("touchend", (e) => this.onTouchEnd(e));
            global.addEventListener("touchcancel", (e) => this.onTouchEnd(e));
        }

        getMaxOffsets() {
            const pane = this.panes[0];
            if (!pane) return { maxX: 0, maxY: 0 };

            const rect = pane.getBoundingClientRect();
            const w = rect.width;
            const h = rect.height;
            const extraScale = this.state.scale - 1;

            if (extraScale <= 0) {
                return { maxX: 0, maxY: 0 };
            }

            return {
                maxX: (w * extraScale) / 2,
                maxY: (h * extraScale) / 2,
            };
        }

        clampOffsets() {
            const { maxX, maxY } = this.getMaxOffsets();

            this.state.offsetX = Math.max(
                -maxX,
                Math.min(maxX, this.state.offsetX)
            );
            this.state.offsetY = Math.max(
                -maxY,
                Math.min(maxY, this.state.offsetY)
            );

            if (this.state.scale <= 1) {
                this.state.offsetX = 0;
                this.state.offsetY = 0;
            }
        }

        onWheel(e) {
            e.preventDefault();

            const delta = e.deltaY;
            const zoomFactor = delta < 0 ? 1.1 : 0.9;
            let newScale = this.state.scale * zoomFactor;
            newScale = Math.max(this.MIN_SCALE, Math.min(this.MAX_SCALE, newScale));

            this.state.scale = newScale;
            this.clampOffsets();
            this.applyTransform();
            this.updateStatus();
        }

        onDragStart(e) {
            if (this.state.scale <= 1) return;

            e.preventDefault();
            this.dragging.active = true;
            this.dragging.startX = e.clientX;
            this.dragging.startY = e.clientY;
            this.dragging.originX = this.state.offsetX;
            this.dragging.originY = this.state.offsetY;
        }

        onDragMove(e) {
            if (!this.dragging.active) return;
            const dx = e.clientX - this.dragging.startX;
            const dy = e.clientY - this.dragging.startY;

            this.state.offsetX = this.dragging.originX + dx;
            this.state.offsetY = this.dragging.originY + dy;

            this.clampOffsets();
            this.applyTransform();
            this.updateStatus();
        }

        onDragEnd() {
            this.dragging.active = false;
        }

        getSingleTouchPoint(e) {
            const t = e.touches[0] || e.changedTouches[0];
            if (!t) return null;
            return { x: t.clientX, y: t.clientY };
        }

        getTouchDistance(e) {
            if (e.touches.length < 2) return 0;
            const t1 = e.touches[0];
            const t2 = e.touches[1];
            const dx = t2.clientX - t1.clientX;
            const dy = t2.clientY - t1.clientY;
            return Math.hypot(dx, dy);
        }

        onTouchStart(e) {
            if (e.touches.length === 1) {
                if (this.state.scale <= 1) return;
                const p = this.getSingleTouchPoint(e);
                if (!p) return;
                e.preventDefault();

                this.touchState.mode = "drag";
                this.touchState.startX = p.x;
                this.touchState.startY = p.y;
                this.touchState.originX = this.state.offsetX;
                this.touchState.originY = this.state.offsetY;
            } else if (e.touches.length >= 2) {
                const dist = this.getTouchDistance(e);
                if (!dist) return;
                e.preventDefault();

                this.touchState.mode = "pinch";
                this.touchState.startDist = dist;
                this.touchState.startScale = this.state.scale;
            }
        }

        onTouchMove(e) {
            if (!this.touchState.mode) return;

            if (this.touchState.mode === "drag" && e.touches.length === 1) {
                const p = this.getSingleTouchPoint(e);
                if (!p) return;
                e.preventDefault();

                const dx = p.x - this.touchState.startX;
                const dy = p.y - this.touchState.startY;

                this.state.offsetX = this.touchState.originX + dx;
                this.state.offsetY = this.touchState.originY + dy;

                this.clampOffsets();
                this.applyTransform();
                this.updateStatus();
            } else if (this.touchState.mode === "pinch" && e.touches.length >= 2) {
                const dist = this.getTouchDistance(e);
                if (!dist || !this.touchState.startDist) return;
                e.preventDefault();

                let newScale =
                    this.touchState.startScale * (dist / this.touchState.startDist);
                newScale = Math.max(this.MIN_SCALE, Math.min(this.MAX_SCALE, newScale));
                this.state.scale = newScale;

                this.clampOffsets();
                this.applyTransform();
                this.updateStatus();
            } else {
                this.onTouchEnd(e);
            }
        }

        onTouchEnd(e) {
            if (e.touches.length === 0) {
                this.touchState.mode = null;
            } else if (e.touches.length === 1 && this.touchState.mode === "pinch") {
                this.touchState.mode = null;
            }
        }

        applyTransform() {
            const { scale, offsetX, offsetY } = this.state;
            const transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
            this.images.forEach((img) => {
                if (!img) return;
                img.style.transform = transform;
            });
        }

        updateStatus() {
            if (!this.statusEl) return;
            this.statusEl.textContent = `缩放: ${this.state.scale.toFixed(
                2
            )}x | 平移: (${this.state.offsetX.toFixed(
                0
            )}, ${this.state.offsetY.toFixed(0)})`;
        }
    }

    // 对外暴露一个简单的 init 方法
    const ImageCompare = {
        init(root, imageGroups) {
            if (!root) return null;
            return new SynchronizedImageCompare(root, imageGroups);
        },
    };

    global.ImageCompare = ImageCompare;
})(window);
