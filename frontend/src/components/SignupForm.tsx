import { useForm, SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import SignupFormSchema, { SignupFormData } from '@/schemas/SignupFormSchema';
import toast from 'react-hot-toast';

// signup form component, requiring email, username and password
// zod validation schema is used to validate the form

function SignupForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupFormData>({
    resolver: zodResolver(SignupFormSchema),
  })

  const API_URL = import.meta.env.VITE_API_URL;

  const onSubmit: SubmitHandler<SignupFormData> = async (data) => {
    try {
      const response = await fetch(`${API_URL}/api/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      const result = await response.json();

      if (response.ok) {
        toast.success(result.message || 'Signup successful!');
      } else {
        toast.error(result.message || 'Signup failed. Please try again.');
      }
    } catch (error) {
      toast.error('An error occurred. Please try again later.');
      console.error('Signup error:', error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center bg-[var(--color-base)]">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="flex flex-col items-center justify-center gap-4"
      >
        <input {...register('email')} type="email" placeholder="Email" className="mb-4 p-2 border border-gray-300 rounded" />
        <p>{errors.email?.message}</p>

        <input {...register('username')} type="text" placeholder="Username" className="mb-4 p-2 border border-gray-300 rounded" />
        <p>{errors.username?.message}</p>

        <input {...register('password')} type="password" placeholder="Password" className="mb-4 p-2 border border-gray-300 rounded" />
        <p>{errors.password?.message}</p>

        <input {...register('confirmPassword')} type="password" placeholder="Confirm Password" className="mb-4 p-2 border border-gray-300 rounded" />
        <p>{errors.confirmPassword?.message}</p>

        <button
          className="px-4 py-2 rounded-sm bg-[var(--color-base2)] hover:bg-[var(--color-base3)] font-semibold transition-colors duration-300"
          type="submit">Submit</button>
      </form>
    </div>
  )
}

export default SignupForm

