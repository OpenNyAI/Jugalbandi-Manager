import { createContext, useContext, useEffect, useState } from 'react';
import { 
    User,
    AuthMethodKey,
    AuthContextData,
    AuthProviderProps,
    IAuth,
    AuthMethod
} from './auth.model';

export const AuthContext = createContext<AuthContextData>(
    {} as AuthContextData,
);

export function AuthProvider({ children }: AuthProviderProps) {
    const [user, setUser] = useState<User>();
    const [authMethod, setAuthMethod] = useState<AuthMethodKey>('MS');
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        createAuthMethodFromStorage();
    }, []);


    async function createAuthMethodFromStorage(){
        const storageMethod = await localStorage.getItem('@Auth.method');
        if(storageMethod) {
            const method = storageMethod as AuthMethodKey;
            const auth = AuthMethod[method];
            setAuthMethod(method);
        }
    }

    const getAuthMethodType = () => {
        return authMethod.toString().toLowerCase();
    }

    useEffect(() => {
        setAuthenticationStatus();
    }, [authMethod]);

    async function setAuthenticationStatus() {
        if (authMethod) {
            const auth = AuthMethod[authMethod];
            const authenticated = await auth.isAuthenticated();
            setIsAuthenticated(authenticated);
        }
    }

    const logIn = async (method: AuthMethodKey, code?: string) => {
        localStorage.setItem('@Auth.method', method);
        const auth = AuthMethod[method];
        await auth.logIn(code);
        setAuthMethod(method);
    }

    const logOut = async () => {
        if (authMethod) {
            const auth = AuthMethod[authMethod];
            await auth?.logOut();
            localStorage.removeItem('@Auth.method');
        }
    }

    const getToken = async() => {
        if(authMethod) {
            const auth = AuthMethod[authMethod];
            return await auth.getToken();
        }
        return undefined;
    }

    return (
        <AuthContext.Provider 
            value={{ user, logIn, logOut, isAuthenticated, getAuthMethodType, getToken }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);