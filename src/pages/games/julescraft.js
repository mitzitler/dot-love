import React, { lazy, Suspense } from "react";
import { NavLink } from "react-router-dom";
import { CardStackPage } from "../../components/CardStackPage";
import { CardStackFooter } from "../../components/CardStackFooter";

const JulesCraftThree = lazy(() =>
  import("../../components/games/JulesCraftThree")
);

export function JulesCraft() {
  const pageMainColor = "plum";
  const pageSecondaryColor = "cyan";
  const pageTertiaryColor = "terracotta";
  const pageSection = "games";

  return (
    <>
      <CardStackFooter
        pageMainColor={pageMainColor}
        pageSecondaryColor={pageSecondaryColor}
        pageTertiaryColor={pageTertiaryColor}
      >
        <NavLink to="/" className="btn-23">
          <marquee>INFO ←</marquee>
        </NavLink>
      </CardStackFooter>
      <CardStackPage
        pageMainColor={pageMainColor}
        pageSecondaryColor={pageSecondaryColor}
        pageTertiaryColor={pageTertiaryColor}
        pageSection={pageSection}
        customClass="game-card"
      >
        <div
          style={{
            height: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            padding: "15px 20px 150px 40px",
            overflow: "hidden",
          }}
        >
          <h2 style={{ color: "#fff", marginBottom: 8 }}>JulesCraft</h2>
          <p style={{ color: "#ddd", marginBottom: 16, textAlign: "center" }}>
            Click in the scene to lock the mouse. Use WASD or arrows to move.
            Look around with the mouse.
          </p>
          <Suspense
            fallback={
              <div
                style={{
                  color: "#ffffff",
                  textAlign: "center",
                  padding: "40px",
                }}
              >
                Loading 3D world...
              </div>
            }
          >
            <JulesCraftThree />
          </Suspense>
        </div>
      </CardStackPage>
    </>
  );
}

export default JulesCraft;
