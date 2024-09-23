import { RSVPPage, RSVPForm, RSVPFormSubmit } from "./components/RSVPPage";
import { RegistryPage } from "./components/RegistryPage";
import { InfoPage, InfoHeader, InfoBody, Schedule } from "./components/InfoPage";
import { useState } from "react";

const temp_data = [
  {
    full_name: "pritham_swaminathan",
    f_name: "pritham",
    state: "ny",
    city: "new york",
    is_local: true,
    status: "best_man",
    accompanied: true,
    rsvp: false,
  },
  {
    full_name: "stephanie_zitler",
    f_name: "stephanie",
    state: "la",
    city: "new orleans",
    is_local: false,
    status: "close_family",
    accompanied: false,
    rsvp: false,
  },
  {
    full_name: "lou_hewitt",
    f_name: "lou",
    state: "ny",
    city: "new_york",
    is_local: true,
    status: "bridesmaid",
    accompanied: true,
    rsvp: false,
  },
];

export default function App() {
  /*
  const guest = [
    profile.name: full_name,
    profile.name[0]: f_name,
    profile.state: state,
    profile.city: city,
    is local,
    sheet.status = status // either bridesmain, groomsman, family, other
    accompanied = true // or false,
    rsvp = true // or false
  ]
  */
  const [rsvpCode, setRsvpCode] = useState("");

  const guest = temp_data;
  const guestStatus = "family";
  const isLocal = true;
  const code = "AXZC";

  return (
    <div>
      
      {/* <RSVPPage position = "absolute" height = "100"> */}
  
        {/* conditionally need to render this invisible if rsvp = true */}
        
        {/* <Header>
        </Header>
        <Body>
          {" "}
          <RSVPForm rsvpCode={rsvpCode} />
        </Body>
        <Footer>
          <ContactRequest />
        </Footer>
      </RSVPPage>
       */}
      {/* conditionally need to render everything below as invisible if rsvp = false */}
      {/* i should use the class name timeline for the schedule! */}
{/*
      <InfoPage>
      
      
        <Header>
          <InfoHeader>tHiS Is WhErE wE wIlL tElL yOu EvErYtHiNg</InfoHeader>
        </Header>
        <Body>
          <InfoBody guestStatus={guestStatus} isLocal={isLocal} />
          <Schedule guestStatus={guestStatus} isLocal={isLocal} />
        </Body>
        <Footer>
          <ContactRequest />
        </Footer>
      </InfoPage>
  
      <RegistryPage />
      <Header>oUr ReGiStRy, wItH lOtS oF OpTiOnS</Header>
        <Body>
          <Text />
          <GiftGraph />
          <GiftSelector />
        </Body>
        <Footer>
          <ContactRequest />
        </Footer>
*/}
     <RegistryPage />
{/*
      <DataPage>
        <Header>i Am CoLlEcTiNg DaTa On AlL yAlL</Header>
        <Body>
          <Text />
          <Graphic key={1} />
          <Graphic key={2} />
          <Graphic key={3} />
          <Graphic key={4} />
          <Graphic key={5} />
          <Graphic key={6} />
          <Text />
        </Body>
        <Footer>
          <ContactRequest />
        </Footer>
      </DataPage>

      <ThanksPage>
        <Header />
        <Body>
          <Text />
        </Body>
        <Footer>
          <ContactRequest />
        </Footer>
      </ThanksPage>
  */}
    </div>
  );
}

function Header({ children }) {
  return <div>{children}</div>;
}

function Body({ children }) {
  return <div>{children}</div>;
}

function Footer({ children }) {
  return <div>{children}</div>;
}

function ContactRequest({ children }) {
  return <div>{children}</div>;
}

function GiftGraph({ children }) {
  return <div>{children}</div>;
}

function GiftSelector({ children }) {
  return <div>{children}</div>;
}

function Text({ children }) {
  return <div>{children}</div>;
}

function Graphic({ children }) {
  return <div>{children}</div>;
}

function ThanksPage({ children }) {
  return <div>{children}</div>;
}

function DataPage({ children }) {
  return <div>{children}</div>;
}
