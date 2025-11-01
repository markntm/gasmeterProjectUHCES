import cv2
import numpy as np
import math
from pathlib import Path

# Toggle this to see GUI windows (handy on a laptop; leave False on a headless Pi)
SHOW_WINDOWS = False


# ========== UTILITY FUNCTIONS ==========


def avg_circles(circles, b):
    avg_x = sum(circles[0][i][0] for i in range(b)) / b
    avg_y = sum(circles[0][i][1] for i in range(b)) / b
    avg_r = sum(circles[0][i][2] for i in range(b)) / b
    return int(avg_x), int(avg_y), int(avg_r)


def dist_2_pts(x1, y1, x2, y2):
    return float(np.hypot(x2 - x1, y2 - y1))


def line_center_distance(cx, cy, x1, y1, x2, y2):
    num = abs((y2 - y1)*cx - (x2 - x1)*cy + x2*y1 - y2*x1)
    den = math.hypot(y2 - y1, x2 - x1)
    return num / (den + 1e-6)


def angle_deg_from_center(cx, cy, tipx, tipy):
    # 0° = up; increases CLOCKWISE (0 at top, 1 to the right, ...)
    dx, dy = tipx - cx, tipy - cy
    ang = math.degrees(math.atan2(dx, -dy))
    return (ang + 360.0) % 360.0


def draw_tick_marks(img, x, y, r, zero_angle=0):
    """
    Draw 0..9 ticks. zero_angle in degrees; 0° points up.
    Angles increase CLOCKWISE to match printed digits.
    Returns: list of (angle_deg, value, label_x, label_y)
    """
    tick_marks = []
    for i in range(10):
        angle_deg = (zero_angle + i * 36) % 360
        ang = math.radians(angle_deg)
        inner = (int(x + 0.85 * r * math.sin(ang)), int(y - 0.85 * r * math.cos(ang)))
        outer = (int(x + 1.00 * r * math.sin(ang)), int(y - 1.00 * r * math.cos(ang)))
        label = (int(x + 1.15 * r * math.sin(ang)), int(y - 1.15 * r * math.cos(ang)))
        cv2.line(img, inner, outer, (0, 255, 0), 2)
        cv2.putText(img, str(i), label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        tick_marks.append((angle_deg, i, label[0], label[1]))
    return tick_marks


def hstack_same_height(a, b):
    h1, w1 = a.shape[:2]; h2, w2 = b.shape[:2]
    if h1 == h2: return np.hstack((a, b))
    if h1 > h2:
        pad = np.zeros((h1 - h2, w2, 3), dtype=b.dtype); b = np.vstack((b, pad))
    else:
        pad = np.zeros((h2 - h1, w1, 3), dtype=a.dtype); a = np.vstack((a, pad))
    return np.hstack((a, b))


def vstack_same_width(a, b):
    h1, w1 = a.shape[:2]; h2, w2 = b.shape[:2]
    if w1 == w2: return np.vstack((a, b))
    if w1 > w2:
        pad = np.zeros((h2, w1 - w2, 3), dtype=b.dtype); b = np.hstack((b, pad))
    else:
        pad = np.zeros((h1, w2 - w1, 3), dtype=a.dtype); a = np.hstack((a, pad))
    return np.vstack((a, b))


def maybe_show(title, img):
    if SHOW_WINDOWS:
        cv2.imshow(title, img); cv2.waitKey(0)


# ========== MAIN FUNCTIONS ==========


def calibrate_gauge(gauge_img, zero_angle=0):
    if isinstance(gauge_img, np.ndarray):
        img = gauge_img.copy()
        filename = "gauge_input"
    else:
        img = cv2.imread(str(gauge_img))
        if img is None:
            raise FileNotFoundError(f"Could not read {gauge_img}")
        filename = gauge_img

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)

    circles = cv2.HoughCircles(
        gray_blur, cv2.HOUGH_GRADIENT, dp=1.2, minDist=min(h, w)//2,
        param1=120, param2=40,
        minRadius=int(0.30 * h), maxRadius=int(0.55 * h)
    )
    if circles is None:
        print("❌ No circle detected.")
        return None

    a, b, _ = circles.shape
    x, y, r = avg_circles(circles, b)

    vis = img.copy()
    cv2.circle(vis, (x, y), r, (0, 0, 255), 2)
    cv2.circle(vis, (x, y), 4, (0, 0, 255), -1)
    cv2.putText(vis, "Detected dial circle", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
    tick_list = draw_tick_marks(vis, x, y, r, zero_angle=zero_angle)

    # Save + show
    out_cal = Path(filename).with_suffix("").as_posix() + "-calibration.png"
    # cv2.imwrite(out_cal, vis)
    maybe_show("Calibration", vis)

    return x, y, r, tick_list, vis


def get_current_value(img, x, y, r, tick_list, outname, zero_angle=0):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold + cleanup
    bin_adapt = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY_INV, 31, 10)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binary = cv2.morphologyEx(bin_adapt, cv2.MORPH_OPEN, kernel, iterations=1)

    # Masks
    hub_mask = np.ones_like(binary) * 255
    cv2.circle(hub_mask, (x, y), int(0.30 * r), 0, -1)
    binary_hub = cv2.bitwise_and(binary, binary, mask=hub_mask)

    ring_mask = np.zeros_like(binary_hub)
    cv2.circle(ring_mask, (x, y), int(1.15 * r), 255, -1)
    cv2.circle(ring_mask, (x, y), int(0.15 * r), 0, -1)
    binary_ring = cv2.bitwise_and(binary_hub, ring_mask)

    panel_binary = cv2.cvtColor(binary_ring, cv2.COLOR_GRAY2BGR)
    cv2.putText(panel_binary, "Preprocessed (binary) for needle", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    # cv2.imwrite(Path(outname).with_suffix("").as_posix() + "-binary.png", panel_binary)
    maybe_show("Binary", panel_binary)

    # Lines
    lines = cv2.HoughLinesP(binary_ring, rho=1, theta=np.pi/180, threshold=60,
                            minLineLength=int(0.20 * r), maxLineGap=6)

    panel_lines = img.copy()
    if lines is not None:
        for L in lines:
            x1, y1, x2, y2 = L[0]
            cv2.line(panel_lines, (x1, y1), (x2, y2), (0, 255, 255), 1)
    cv2.putText(panel_lines, "All candidate lines", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
    # cv2.imwrite(Path(outname).with_suffix("").as_posix() + "-lines.png", panel_lines)
    maybe_show("All Lines", panel_lines)

    # Filter + score
    candidates = []
    if lines is not None:
        for L in lines:
            x1, y1, x2, y2 = L[0]
            d1 = dist_2_pts(x, y, x1, y1)
            d2 = dist_2_pts(x, y, x2, y2)
            dn, df = (d1, d2) if d1 < d2 else (d2, d1)
            if not (0.20 * r < dn < 0.45 * r and 0.60 * r < df < 1.25 * r):
                continue
            lc = line_center_distance(x, y, x1, y1, x2, y2)
            length = dist_2_pts(x1, y1, x2, y2)
            score = length - 8.0 * lc
            candidates.append((score, [x1, y1, x2, y2]))

    panel_candidates = img.copy()
    if candidates:
        for _, L in candidates:
            cv2.line(panel_candidates, (L[0], L[1]), (L[2], L[3]), (0, 255, 0), 2)
    cv2.putText(panel_candidates, "Needle-like candidates", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
    # cv2.imwrite(Path(outname).with_suffix("").as_posix() + "-candidates.png", panel_candidates)
    maybe_show("Candidates", panel_candidates)

    if not candidates:
        print("❌ No needle-like line after scoring.")
        return None, panel_binary, panel_lines, panel_candidates

    # Best line
    candidates.sort(key=lambda t: -t[0])
    x1, y1, x2, y2 = candidates[0][1]
    tip = (x1, y1) if dist_2_pts(x, y, x1, y1) > dist_2_pts(x, y, x2, y2) else (x2, y2)

    # Angle-based snapping
    ang = angle_deg_from_center(x, y, tip[0], tip[1])
    value = int((ang + 18.0) // 36.0) % 10

    # Final overlay
    vis = img.copy()
    cv2.circle(vis, (x, y), r, (0, 0, 255), 2)
    draw_tick_marks(vis, x, y, r, zero_angle=zero_angle)
    cv2.line(vis, (x1, y1), (x2, y2), (255, 0, 0), 2)
    cv2.arrowedLine(vis, (x, y), tip, (255, 0, 0), 2, tipLength=0.15)
    cv2.circle(vis, tip, 6, (0, 0, 255), -1)
    cv2.putText(vis, f"Angle: {ang:.1f} deg", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 128, 0), 2, cv2.LINE_AA)
    cv2.putText(vis, f"Reading: {value}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 128, 0), 2, cv2.LINE_AA)

    out_final = Path(outname).with_suffix("").as_posix() + "-needle.png"
    # cv2.imwrite(out_final, vis)
    maybe_show("Final", vis)

    return value, panel_binary, panel_lines, panel_candidates


def save_storyboard(panel_circle, panel_binary, panel_lines, panel_candidates, outname):
    row1 = hstack_same_height(panel_circle, panel_binary)
    row2 = hstack_same_height(panel_lines, panel_candidates)
    board = vstack_same_width(row1, row2)
    out_story = Path(outname).with_suffix("").as_posix() + "-storyboard.png"
    # cv2.imwrite(out_story, board)
    maybe_show("Storyboard", board)


# ========== MAIN ==========
# @TODO future: program still miss-reads the arrows direction, make sure it only reads the longest detection of the arrow
# @TODO future: take in parameter of previous gauge value to help in reading when between two values


def r_main(gauge_img, counter_clockwise):
    zero_angle = 0 # adjust if the photo is rotated; 0° = up

    calib = calibrate_gauge(gauge_img, zero_angle=zero_angle)
    if calib is None:
        return 0
    x, y, r, tick_list, panel_circle = calib

    value, panel_binary, panel_lines, panel_candidates = get_current_value(
        gauge_img, x, y, r, tick_list, "gauge_input", zero_angle=zero_angle
    )
    if value is None:
        print("Could not determine the reading.")
        return 0

    if counter_clockwise:
        value = 9 - value

    save_storyboard(panel_circle, panel_binary, panel_lines, panel_candidates, "gauge_input")

    if SHOW_WINDOWS:
        cv2.destroyAllWindows()

    return value
