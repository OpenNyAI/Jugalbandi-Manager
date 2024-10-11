import { Routes, Route, useLocation, useParams } from "react-router-dom";
import Navbar from "./components/navbar/navbar";
import Home from "./pages/home/home";
import Chat from "./pages/chat";
import Analytics from "./pages/analytics";
import { useEffect } from "react";
import { BotSettings } from "./pages/BotSettings/BotSettings";

function Router() {
    let location = useLocation();

    useEffect(() => {
        const navItems = document.getElementById("navbar")?.children as HTMLCollectionOf<HTMLElement>;
        if(!navItems) return;
        for(var i=0; i<navItems.length; i++) {
            navItems[i].style.background = "#FFF";
            navItems[i].style.fill = "#B6B6B6";
        }

        switch (location.pathname) {
            case "/":
                const homeNav = document.getElementById("homeNav") as HTMLElement;
                homeNav.style.background = "#EBE7FF";
                homeNav.style.fill = "#7F63FF";
                break;
            case "/chat":
                const chatNav = document.getElementById("chatNav") as HTMLElement;
                chatNav.style.background = "#EBE7FF";
                chatNav.style.fill = "#7F63FF";
                break;
            case "/analytics":
                const analyticsNav = document.getElementById("analyticsNav") as HTMLElement;
                analyticsNav.style.background = "#EBE7FF";
                analyticsNav.style.fill = "#7F63FF";
                break;
            case `/settings/${location.pathname.split("/")[2]}`:
                const settingsNav = document.getElementById("settingsNav") as HTMLElement;
                settingsNav.style.background = "#EBE7FF";
                settingsNav.style.fill = "#7F63FF";
                break;
        }
    },[location]);

    return (
        <Routes>
            <Route path="/" element={<Navbar />}>
                <Route index element={<Home />} />
                <Route path="chat" element={<Chat />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="settings" element={<BotSettingsWrapper />} />
                <Route path="settings/:botID" element={<BotSettingsWrapper />} />
                <Route path="*" element={<NoPage />} />
            </Route>
        </Routes>
    );
}

export default Router;

const NoPage = () => {
    return <h1 style={{width: '100vw', textAlign: 'center'}}>Page does not exist !</h1>;
};
const BotSettingsWrapper = () => {
    const { botID } = useParams();
    return <BotSettings botID={botID} />;
};