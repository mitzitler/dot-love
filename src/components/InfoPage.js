//
export function InfoPage({ children }) {
  return <div>{children}</div>;
}

export function InfoHeader({ children }) {
  return <div>{children}</div>;
}

export function InfoBody({}) {
  return (
    <div>
      <h2>Attire</h2>
      <h2>Travel information</h2>
      {/* if isLocal = true then give train information, if isLocal = false then hotel information */}
      <h2>FAQs</h2>
    </div>
  );
}

export function Schedule({}) {
  return (
    <div>
      <h3>This is our wedding day schedule as we know it so far</h3>
      {/* conditional rendering if the guest is in the wedding party for morning of */}
      {/* conditional rendering if the guest is in the wedding party or family for photos */}
      <ul>Six pm: Guests arrive at Diety</ul>
      <ul>Six thirty pm: Ceremony starts</ul>
      <ul>Seven pm: Cocktail hour</ul>
      <ul>Eight pm: Dinner</ul>
      <ul>
        Nine pm: Dancing, photos, whatever. We have the space until midnight!
      </ul>
      <ul>
        We will tear up the night next door after we get kicked out of Diety.
        Come through!
      </ul>
      {/* conditional rending if the guest is in the wedding party or not local */}
      <h3>Extracurriculars</h3>
      <ul>Rehersal dinner</ul>
      <ul>Saturday brunch for out of town</ul>
    </div>
  );
}
