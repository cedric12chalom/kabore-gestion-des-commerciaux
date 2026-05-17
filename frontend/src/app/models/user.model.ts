export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name?: string;
  role: 'ADMIN' | 'MANAGER' | 'COMMERCIAL';
  role_display?: string;
  phone?: string;
  photo?: string | null;
  is_active: boolean;
  manager?: number | null;
  team_count?: number;
  date_joined: string;
  last_modified?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface ChangePasswordData {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
}
