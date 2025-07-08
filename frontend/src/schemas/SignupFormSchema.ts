// schema for signup form validation, requiering email and name

import { z } from 'zod';

const SignupFormSchema = z.object({
  email: z.string().email('Invalid email address'),
  username: z.string().min(3, 'Username must be at least 3 characters long'),
  password: z.string().min(8, 'Password must be at least 8 characters long'),
})

export type SignupFormData = z.infer<typeof SignupFormSchema>;
export default SignupFormSchema;

