    getUser: () => Promise<User | undefined>;
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
    const [isLoading, setIsLoading] = useState(true);
    const [user, setUser] = useState<User>();
    const [authMethod, setAuthMethod] = useState<IAuth>();
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        createAuthMethodFromStorage();
    }, []);


    async function createAuthMethodFromStorage(){
        const storageMethod = await localStorage.getItem('@Auth.method');
        if(storageMethod) {
            const method = storageMethod as AuthMethodKey;
            const auth = AuthMethod[method];
            setAuthMethod(auth);
        }
    }

    const getAuthMethodType = () => {
        return authMethod?.type.toLowerCase() as string;
    }

    useEffect(() => {
        setAuthenticationStatus();
        setIsLoading(false);
    }, [authMethod]);

    async function setAuthenticationStatus() {
        if (authMethod) {
            const authenticated = await authMethod.isAuthenticated();
            setIsAuthenticated(authenticated);
            if (authenticated) {
                await setUserLogged(authMethod);
            }
        }
    }

    const logIn = async (method: AuthMethodKey, code?: string) => {
        localStorage.setItem('@Auth.method', method);
        const auth = AuthMethod[method];
        await auth.logIn(code);
        setAuthMethod(auth);
    }

    const logOut = async () => {
        if (authMethod) {
            await authMethod?.logOut();
            localStorage.removeItem('@Auth.method');
            setIsAuthenticated(false);
        }
    }

    const getToken = async() => {
        if(authMethod) {
            return await authMethod.getToken();
        }
        return undefined;
    }

    async function setUserLogged(authMethod:IAuth) {
        const user = await authMethod.getUser();
        setUser(user);
    }

    async function getUser() {
        if (!user && authMethod) {
               setUserLogged(authMethod);
        }
        return user;
    }

    return (
        <AuthContext.Provider 
            value={{ user, logIn, logOut, isAuthenticated, getAuthMethodType, getToken, getUser, isLoading }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);