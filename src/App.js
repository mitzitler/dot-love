import { RSVPPage, RSVPForm, RSVPFormSubmit } from "./components/RSVPPage";
import { RegistryPage } from "./components/RegistryPage";
import { InfoBody } from "./components/InfoBody";
import { ThanksBody } from "./components/ThanksBody";
import { AboutUsBody } from "./components/AboutUsBody";
import { useState } from "react";
import { GenericPage } from "./components/GenericPage";
import Info from "three/src/renderers/common/Info.js";

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

  // page = 0 is rsvp. this increments
  const [pageNum, setPageNum] = useState(1)
  const pageMax = 4

  function handleNavClick() {
    console.log('You clicked me')
    console.log(pageNum)
    if (pageNum < pageMax) {
      setPageNum(pageNum+1)
    } else {
      setPageNum(1)
    };
  }

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
  
*/}  
    {pageNum === 1 && <>
      <GenericPage id="1" 
        handleNavClick={handleNavClick}
        leftSide="info left"
        rightSide="info right"
      />
      <InfoBody/>
    </>}
    {pageNum === 2 && <RegistryPage id="2" 
      handleNavClick={handleNavClick}
      leftSide="buy me gifts now"
      rightSide="or you will be cursed"
      />}
    {pageNum === 3 && <>
      <GenericPage id="3" 
        handleNavClick={handleNavClick}
        leftSide="thank you left"
        rightSide="thank you right"
      />
      <ThanksBody/>
    </>}
    {pageNum === 4 && <>
      <GenericPage id="4" 
        handleNavClick={handleNavClick}
        leftSide="about us left"
        rightSide="about us right"
      />
      <AboutUsBody />
    </>}
{/*


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

function Text({ children }) {
  return <div>{children}</div>;
}

function Graphic({ children }) {
  return <div>{children}</div>;
}

function ThanksPage({ children }) {
  return <div>{children}</div>;
}