import React from "react";
import {
  Composition,
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Easing,
  Sequence,
} from "remotion";
import {
  TransitionSeries,
  springTiming,
} from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont("normal", {
  weights: ["300", "400", "500", "600", "700", "800"],
  subsets: ["latin"],
});

const COLORS = {
  bg: "#0a0a0f",
  surface: "#141419",
  border: "#1e1e26",
  accent: "#6366f1",
  accentBlue: "#4f46e5",
  text: "#e8e8ed",
  muted: "#6b6b7b",
  green: "#22c55e",
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: "100%",
    height: "100%",
    backgroundColor: COLORS.bg,
    fontFamily,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
    overflow: "hidden",
  },
  gradientText: {
    fontWeight: 800,
    background: `linear-gradient(135deg, ${COLORS.accent}, ${COLORS.accentBlue})`,
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
};

const Orbs: React.FC = () => (
  <>
    <div
      style={{
        position: "absolute",
        width: 500,
        height: 500,
        borderRadius: "50%",
        background: COLORS.accent,
        filter: "blur(100px)",
        opacity: 0.12,
        top: -150,
        left: -150,
      }}
    />
    <div
      style={{
        position: "absolute",
        width: 400,
        height: 400,
        borderRadius: "50%",
        background: COLORS.accentBlue,
        filter: "blur(100px)",
        opacity: 0.1,
        bottom: -100,
        right: -100,
      }}
    />
  </>
);

const SCENE_DURATION = 4; // seconds each (total = 12s)
const FADE_DURATION = 1; // seconds for transition

const Scene1: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = interpolate(frame, [0, fps], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scale = interpolate(enter, [0, 1], [0.85, 1]);

  return (
    <AbsoluteFill style={styles.container}>
      <Orbs />
      <div
        style={{
          transform: `scale(${scale})`,
          opacity: enter,
          textAlign: "center",
          padding: "0 120px",
        }}
      >
        <div
          style={{
            fontSize: 60,
            fontWeight: 400,
            color: COLORS.text,
            lineHeight: 1.3,
            letterSpacing: "-0.5px",
          }}
        >
          ¿Quieres llevar tu{" "}
          <span style={styles.gradientText}>inglés</span> al siguiente nivel?
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Scene2: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const translateY = interpolate(frame, [0, fps * 0.8], [200, 0], {
    easing: Easing.bezier(0.22, 1, 0.36, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const opacity = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={styles.container}>
      <Orbs />
      <div
        style={{
          transform: `translateY(${translateY}px)`,
          opacity,
          textAlign: "center",
          padding: "0 120px",
        }}
      >
        <div
          style={{
            fontSize: 46,
            fontWeight: 400,
            color: COLORS.text,
            lineHeight: 1.4,
          }}
        >
          Descubre{" "}
          <span style={{ ...styles.gradientText, fontSize: 54 }}>
            Verb Trainer
          </span>
        </div>
        <div
          style={{
            marginTop: 24,
            fontSize: 32,
            color: COLORS.muted,
            fontWeight: 300,
            lineHeight: 1.5,
          }}
        >
          y aprende inglés de forma{" "}
          <span style={{ color: COLORS.green, fontWeight: 500 }}>sencilla</span>{" "}
          y{" "}
          <span style={{ color: COLORS.accent, fontWeight: 500 }}>
            divertida
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Scene3: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoScale = spring({
    frame: Math.max(0, frame - fps * 0.3),
    fps,
    config: { damping: 14, stiffness: 90, mass: 0.6 },
  });

  const taglineOpacity = interpolate(frame, [fps * 0.6, fps * 1.2], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const ctaOpacity = interpolate(frame, [fps * 1.4, fps * 2], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={styles.container}>
      <Orbs />
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 28,
          transform: `scale(${logoScale})`,
        }}
      >
        <div
          style={{
            fontSize: 72,
            fontWeight: 800,
            background: `linear-gradient(135deg, ${COLORS.accent}, ${COLORS.accentBlue})`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            letterSpacing: "-1px",
          }}
        >
          Verb Trainer
        </div>

        <div
          style={{
            fontSize: 26,
            color: COLORS.muted,
            fontWeight: 400,
            opacity: taglineOpacity,
          }}
        >
          English Irregular Verbs — DevOps Edition
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            marginTop: 12,
            padding: "14px 28px",
            backgroundColor: COLORS.surface,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 12,
            opacity: ctaOpacity,
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={COLORS.accent} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 2v6h-6" />
            <path d="M3 12a9 9 0 0115.36-6.36L21 8" />
            <path d="M3 22v-6h6" />
            <path d="M21 12a9 9 0 01-15.36 6.36L3 16" />
          </svg>
          <span style={{ fontSize: 18, color: COLORS.text, fontWeight: 500 }}>
            github.com/LabordaSebastian/english-verb-trainer
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const PromoVideo: React.FC = () => {
  const { fps } = useVideoConfig();
  const sceneDuration = SCENE_DURATION * fps;
  const fadeDuration = FADE_DURATION * fps;

  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={sceneDuration} premountFor={fps}>
        <Scene1 />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={fade()}
        timing={springTiming({ config: { damping: 200 }, durationInFrames: fadeDuration })}
      />
      <TransitionSeries.Sequence durationInFrames={sceneDuration} premountFor={fps}>
        <Scene2 />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={fade()}
        timing={springTiming({ config: { damping: 200 }, durationInFrames: fadeDuration })}
      />
      <TransitionSeries.Sequence durationInFrames={sceneDuration} premountFor={fps}>
        <Scene3 />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};

export const RemotionRoot: React.FC = () => {
  const fps = 30;
  const sceneDuration = SCENE_DURATION * fps;
  const fadeDuration = FADE_DURATION * fps;
  const totalDuration = sceneDuration * 3 - fadeDuration * 2;

  return (
    <Composition
      id="PromoVideo"
      component={PromoVideo}
      durationInFrames={totalDuration}
      fps={fps}
      width={1920}
      height={1080}
    />
  );
};
