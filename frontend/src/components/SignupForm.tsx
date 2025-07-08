import { useForm, SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import SignupFormSchema, { SignupFormData } from '../schemas/SignupFormSchema';
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

  const onSubmit: SubmitHandler<SignupFormData> = (data) => {
    console.log(data);
    toast.success('Submission successful!');
  }

  return (
    <div className="flex flex-col items-center justify-center bg-[var(--color-base)]">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="flex flex-col items-center justify-center"
      >
        <input {...register('email')} type="email" placeholder="Email" className="mb-4 p-2 border border-gray-300 rounded" />
        <p>{errors.email?.message}</p>

        <input {...register('username')} type="text" placeholder="Username" className="mb-4 p-2 border border-gray-300 rounded" />
        <p>{errors.username?.message}</p>

        <input {...register('password')} type="password" placeholder="Password" className="mb-4 p-2 border border-gray-300 rounded" />
        <p>{errors.password?.message}</p>

        <button
          className="p-4 rounded-sm bg-[var(--color-base2)]"
          type="submit">Submit</button>
      </form>
    </div>
  )
}

export default SignupForm

