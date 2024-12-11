import React from 'react';
import { useForm } from 'react-hook-form';
import { savePlatformCredentials } from '../api/credentials';

interface CredentialFormData {
    access_key?: string;
    secret_key?: string;
    region?: string;
    path?: string;
}

export const PlatformCredentials: React.FC<{ platform: string }> = ({ platform }) => {
    const { register, handleSubmit } = useForm<CredentialFormData>();

    const onSubmit = async (data: CredentialFormData) => {
        try {
            await savePlatformCredentials(platform, data);
            alert('Credentials saved successfully');
        } catch (error) {
            alert('Failed to save credentials');
        }
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)}>
            {platform === 'aws' && (
                <>
                    <input {...register('access_key')} placeholder="Access Key" />
                    <input 
                        {...register('secret_key')} 
                        type="password" 
                        placeholder="Secret Key" 
                    />
                    <input {...register('region')} placeholder="Region" />
                </>
            )}
            <button type="submit">Save Credentials</button>
        </form>
    );
}; 